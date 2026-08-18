/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_multi_precision_mult (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Assign all bidirectional pins as inputs
  assign uio_oe  = 8'b0000_0000;
  assign uio_out = 8'b0000_0000;

  // Assign needed wires
  wire [1:0] mode = uio_in[1:0]; // Multiplier mode, 2-bit, 4-bit, and 8-bit
  wire load_en =    uio_in[2]; // Load enable

  // Assign needed registers
  reg [7:0] op_a_reg;
  reg [15:0] mult_result;
  reg [7:0]  out_reg;

  wire [3:0]  prod_2bit = {2'b0, ui_in[1:0]} * {2'b0, ui_in[3:2]};
  wire [7:0]  prod_4bit = {4'b0, ui_in[3:0]} * {4'b0, ui_in[7:4]};
  wire [15:0] prod_8bit = {8'b0, op_a_reg}   * {8'b0, ui_in};

  assign uo_out = out_reg;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      op_a_reg    <= 8'd0;
      mult_result <= 16'd0;
      out_reg     <= 8'd0;
    end else begin
      case (mode)
        2'b00: begin // 2-bit mode
          mult_result <= {12'b0, prod_2bit};
          out_reg     <= {4'b0,  prod_2bit};
        end

        2'b01: begin // 4-bit mode
          mult_result <= {8'b0, prod_4bit};
          out_reg     <= prod_4bit;
        end

        2'b10: begin // 8-bit mode (2 cycles)
          if (!load_en) begin
            op_a_reg <= ui_in;
            out_reg  <= mult_result[7:0];
          end else begin
            mult_result <= prod_8bit;
            out_reg     <= prod_8bit[15:8];
          end
        end

        default: begin
          out_reg <= 8'd0;
        end
      endcase
    end
  end

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:3], 1'b0};

endmodule
