# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# Changed from default test.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start MAC Test")

    # Set the clock period to 16.67ns (60MHz)
    clock = Clock(dut.clk, 16.67, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0 #load_en = 0, read_sel=0, clr_acc=0
    dut.ena.value = 1
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    #dut.ui_in.value = 20
    #dut.uio_in.value = 30

    # Wait for one clock cycle to see the output values
    #await ClockCycles(dut.clk, 1)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    #assert dut.uo_out.value == 50

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.

    # Make sure that Accumulator starts at absolute 0: 
    dut.uio_in.value = 0x08 #clr_acc = uio[3]
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00 
    await ClockCycles(dut.clk, 1)

    # TEST CASE: 10*5 = 50
    # LOAD A = 10
    dut.ui_in.value = 10
    await cocotb.triggers.ReadOnly() #Wait for signal to stabilize
    dut.uio_in.value= 0x01          # Set load_en (uio[0]) high
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00        # Set load_en low 
    await ClockCycles(dut.clk, 1)

    # LOAD B = 5: 
    dut.ui_in.value = 5
    dut.uio_in.value = 0x01         # set load_en high 
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00         # Set load_en high 

    # Wait for pipeline latency 
    await ClockCycles(dut.clk, 3) 

    # Read the result of accumulator bits [7:0]
    dut.uio_in.value = 0x00 
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 50 
    dut._log.info(f"Successfully calculated 10 * 5 = {int(dut.uo_out.value)}")

    # Test negative numbers: -2 * 10 = -20 
    # Two's complement for -2 (8-bit) is 0xFE (254)
    dut.ui_in.value = 0xFE 
    dut.uio_in.value = 0x01
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00 
    await ClockCycles(dut.clk, 1)

    # Load B = 10 (0x0A)
    dut.ui_in.value= 10
    dut.uio_in.value = 0x01
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00 

    await ClockCycles(dut.clk, 3)

    # Accumulator was not cleared, so 50 + (-20) = 30
    assert dut.uo_out.value == 30
    dut._log.info(f"Accumulated Result Check: {int(dut.uo_out.value)}")