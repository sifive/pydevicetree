# pydevicetree

This is a Python 3 library for parsing, querying, and modifying Devicetree Source v1 files as
described in the [Devicetree Specification v0.2](https://github.com/devicetree-org/devicetree-specification/releases/tag/v0.2).

## Install

pydevicetree supports Python >= 3.5 and can be installed with pip from the [Python Package Index](https://pypi.org/project/pydevicetree/).

`pip install pydevicetree`

## Tutorial

### The Devicetree

Let's say you have a file design.dts with the contents
```
/dts-v1/;

/ {
	#address-cells = <1>;
	#size-cells = <1>;
	compatible = "my,design";
	aliases {
		serial0 = "/soc/uart@10000000";
	};
	chosen {
		stdout-path = "/soc/uart@10000000:115200";
	};
	cpus {
		#address-cells = <1>;
		#size-cells = <0>;
		cpu@0 {
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

#### By path

```
>>> tree.get_by_path("/soc/dtim")
<Node dtim@20000000>
```

Devicetree aliases are allowed in paths

```
>>> tree.get_by_path("serial0")
<Node uart@10000000>
```

#### Getting `Node` properties

The value (or first value of a list/array) of a property can be retrieved with `Node.get_field()`

```
>>> tree.match("sifive,rocket0")[0].get_field("timebase-frequency")
1000000
```

The list or array of values assigned to a property can be retrieved with `Node.get_fields()`

```
>>> tree.match("sifive,rocket0")[0].get_fields("compatible")
<StringList ['sifive,rocket0', 'riscv']>
```

There are helper methods `Node.get_reg()` and `Node.get_ranges()` for the `reg` and `ranges`
Devicetree properties.

```
>>> tree.get_by_path("/soc/dtim").get_reg()
<RegArray [536870912, 268435456]>
>>> tree.get_by_path("/soc/dtim").get_reg().get_by_name("mem")
(536870912, 268435456)
>>> "0x%x" % tree.get_by_path("/soc/dtim").get_reg().get_by_name("mem")[0]
'0x20000000'
```

#### Getting `chosen` properties

`Devicetree.chosen()` provides quick access to the properties of the `chosen` node

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
