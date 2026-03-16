```
varada@silicon:~$ ls -1 projects/
```

```
    OrionRV               → 4-core RV32IM multicore SoC (SystemVerilog)
    rtl-riscv32           → single-cycle RV32I processor
    CMOS-Standard-Cell-Library → transistor-level primitives + 1-bit full adder
    rtl-spi-controller    → full-duplex SPI master/slave, Mode 0
    uart-16bit-verilog    → 16-bit UART TX/RX, even parity, parametric
    rtl-fifo-buffer       → sync FIFO, parameterized depth + status flags
    rtl-single-port-ram   → sync single-port RAM
    rtl-dual-port-ram     → dual-port RAM, independent R/W
    rtl-traffic-controller→ FSM traffic light + emergency override
    rtl-fsm-vending       → FSM vending machine
    veriLogic-HDL         → HDL implementations of core digital logic
    arduino-avoidance-robot → obstacle-avoidance car, ultrasonic + motor
    pingpong-bot          → retro Pong on Arduino
    DinoDash-Arduino      → Chrome Dino runner on OLED/LCD
```

```
varada@silicon:~$ cat stack.txt
```

```
HDL        :  SystemVerilog  Verilog
Simulation :  Vivado  ModelSim  LTspice
Embedded   :  Arduino (C++)
Currently  :  OrionRV — 4-core RISC-V SoC
```

```
varada@silicon:~$ git log --oneline -3
```

```
a1f3c2e  OrionRV: multicore memory consistency
9d82b1a  rtl-riscv32: pipeline hazard handling
4e71dc0  uart-16bit: parametric baud rate
```

---

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=VaradaGovind&show_icons=true&hide_border=true&bg_color=0d1117&title_color=58a6ff&icon_color=58a6ff&text_color=8b949e&count_private=true">
  <img src="https://github-readme-stats.vercel.app/api?username=VaradaGovind&show_icons=true&hide_border=true&bg_color=ffffff&title_color=0969da&icon_color=0969da&text_color=57606a&count_private=true">
</picture>
