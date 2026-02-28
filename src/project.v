/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_8bit_mac(
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
)

    //registers - for simple use cases
    reg[7:0] a_reg, b_reg; 
    reg[15:0] product; 
    reg[23:0] accum; 
    reg load_state; 

    //Control signals 
    wire load_en = uio_in[0]; 
    wire [1:0] read_sel = uio_in[2:1];
    wire clr_acc = uio_in[3]; 

    // Input loading
    always @(posedge clk) begin 
        if (!rst_n) begin 
            a_reg <= 8'h00; 
            b_reg <= 8'h00;
            load_state <= 1'b0; 
        end else if (load_en) begin
            if (load_state == 1'b0)
                a_reg <= ui_in; 
            else 
                b_reg <= ui_in;
            load_state <= ~load_state; 
        end
    end

    // Stage 1: baugh-wooley signed multiplication 
    wire signed [7:0] s_a = a_reg;
    wire signed [7:0] s_b = b_reg;
    wire signed [15:0] product_comb = s_a * s_b; 

    // Stage 2: Baugh Wooley Signed Multiplication
    always @(posedge clk) begin 
        if (!rst_n) 
            product <= 16'h0000;
        else 
            product <= product_comb;
    end

    //Stage 3: 24-bit accumulator with sign extension + guard bits 

    always @(posedge clk) begin 
        if (!rst_n || clr_acc)
            accum <= 24'h000000;
        else 
            accum <= accum + {{8{product[15]}}, product};
    end

    assign uo_out = (read_sel == 2'b00) ? accum[7:0] : 
                    (read_sel == 2'b01) ? accum[15:8] : 
                    (read_sel == 2'b10) ? accum[23:16] : 8'h00;

    assign uio_out = 8'h00;
    assign uio_oe  = 8'h00;


endmodule