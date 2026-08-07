# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

async def reset_dut(dut):
    dut._log.info("Resetting")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    dut._log.info("Reset complete, starting tests")

    dut._log.info("Testing Mode 0 (2-bit)...")
    for a in range(4):
        for b in range(4):
            # ui_in[1:0] = Operand A, ui_in[3:2] = Operand B
            dut.uio_in.value = 0b000  # mode=00, load_en=0
            dut.ui_in.value = (b << 2) | a
            await ClockCycles(dut.clk, 1)

            expected = a * b
            assert dut.uo_out.value == expected, \
                f"Mode 0 Fail: {a} * {b} = {expected}, got {dut.uo_out.value.integer}"


    dut._log.info("Testing Mode 1 (4-bit)...")
    for a in range(16):
        for b in range(16):
            # ui_in[3:0] = Operand A, ui_in[7:4] = Operand B
            dut.uio_in.value = 0b001  # mode=01, load_en=0
            dut.ui_in.value = (b << 4) | a
            await ClockCycles(dut.clk, 1)

            expected = a * b
            assert dut.uo_out.value == expected, \
                f"Mode 0 Fail: {a} * {b} = {expected}, got {dut.uo_out.value.integer}"


    dut._log.info("Testing Mode 2 (8-bit)...")
    for i in range(50): # Test 50 random 8-bit number pairs
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        expected = a * b
        expected_high = (expected >> 8) & 0xFF
        expected_low = expected & 0xFF

        dut.uio_in.value = 0b010
        dut.ui_in.value = a
        await ClockCycles(dut.clk, 1)

        dut.uio_in.value = 0b110
        dut.ui_in.value = b
        await ClockCycles(dut.clk, 1)

        assert dut.uo_out.value == expected_high, \
            f"Mode 2 High Byte Fail: {a} * {b} = {expected} ({hex(expected)}), " \
            f"expected high {hex(expected_high)}, got {hex(dut.uo_out.value.integer)}"

        # Cycle 3: Toggle load_en back to 0 to Read Low Byte (uio_in = 0b010)
        dut.uio_in.value = 0b010
        await ClockCycles(dut.clk, 1)

        # Verify Lower Byte
        assert dut.uo_out.value == expected_low, \
            f"Mode 2 Low Byte Fail: {a} * {b} = {expected} ({hex(expected)}), " \
            f"expected low {hex(expected_low)}, got {hex(dut.uo_out.value.integer)}"

    dut._log.info("All tests passed successfully!")
