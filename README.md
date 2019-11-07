# pydevicetree

This is a Python 3 library for parsing, querying, and modifying Devicetree Source v1 files as
described in the [Devicetree Specification v0.2](https://github.com/devicetree-org/devicetree-specification/releases/tag/v0.2).

## Tutorial

### The Devicetree

Let's say you have a file design.dts with the contents
```
/dts-v1/;

chosen {
	stdout-path = "/soc/uart@10000000:115200";
};

/ {
	#address-cells = <1>;
	#size-cells = <1>;
	compatible = "my,design";
	cpus {
		cpu@0 {
			#size-cells = <0>;
			compatible = "sifive,rocket0", "riscv";
			device_type = "cpu";
			reg = <0>;
			riscv,isa = "rv32imac";
			status = "okay";
			timebase-frequency = <1000000>;
			sifive,dtim = <&dtim>;
			interrupt-controller {
				#interrupt-cells = <1>;
				compatible = "riscv,cpu-intc";
				interrupt-controller;
			};
		};
	};
	soc {
		#address-cells = <1>;
		#size-cells = <1>;
		compatible = "my,design-soc";
		ranges;
		dtim: dtim@20000000 {
			compatible = "sifive,dtim0";
			reg = <0x20000000 0x10000000>;
			reg-names = "mem";
		};
		uart: uart@10000000 {
			compatible = "sifive,uart0";
			reg = <0x10000000 0x1000>;
			reg-names = "control";
		};
	};
};
```

### Parsing the Tree

Parsing the tree is as easy as 1, 2...

```
>>> from pydevicetree import Devicetree
>>> tree = Devicetree.parseFile("design.dts")
>>> tree
<Devicetree my,design>
```

### Querying the Tree

#### By `compatible` string

```
>>> tree.match("sifive,rocket0")
[<Node cpu>]
```

#### Getting `Node` properties

```
>>> tree.match("sifive,rocket0")[0].get_field("timebase-frequency")
1000000
>>> tree.match("sifive,rocket0")[0].get_fields("compatible")
<StringList ['sifive,rocket0', 'riscv']>
```

#### Getting `chosen` properties

```
>>> tree.chosen("stdout-path")
<StringList ['/soc/uart@10000000:115200']>
```

### Converting back to Devicetree

Any tree or subtree can be converted back to Devicetree by calling `Node.to_dts()` or simply
by `print`ing it:

```
>>> print(tree.match("sifive,rocket0")[0])
cpu@0 {
        #size-cells = <0>;
        compatible = "sifive,rocket0", "riscv";
        device_type = "cpu";
        reg = <0x0>;
        riscv,isa = "rv32imac";
        status = "okay";
        timebase-frequency = <1000000>;
        sifive,dtim = <&dtim>;
        interrupt-controller {
                #interrupt-cells = <1>;
                compatible = "riscv,cpu-intc";
                interrupt-controller;
        };
};
```
