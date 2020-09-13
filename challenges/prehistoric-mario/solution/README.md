## Solution

Standard Plattformer Stuff: 11 Boxes with 4 states each can be triggered. The valid combination yields the flag.

`checkFlag` loops each time and appends the current state of the block to an array. The states are: `0, 21, 97, 37`
```
byte data[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

		TiledMapTileLayer layer = (TiledMapTileLayer) map.getLayers().get("questionmarks");
		int counter = 0;

		for (int x = 0; x < 100; x++) {
			for (int y = 0; y < 100; y++) {
				Cell cell = layer.getCell((int) x, (int) y);
				if (cell == null || cell.getTile().getProperties().containsKey("questionmarkType") == false)
					continue;

				int currentType = (int) cell.getTile().getProperties().get("questionmarkType");
				if (currentType == 1337) {
					continue;
				}
				data[counter] = (byte) currentType;
				counter++;
			}
		}

		BigInteger checkResult = new BigInteger(data);
        ```
The result is an BigInteger `x`, constructed from those states. If `x**4` == `415526195901721479409508441149638655484370976826478137498293604962478662570210950312335798465989114801`, the valid state is found. Hence the user has to calculate:
`415526195901721479409508441149638655484370976826478137498293604962478662570210950312335798465989114801**0.25``` (e.g. with Wolfram alpha) == `25389234218165158887367957`
```
>>> a = 25389234218165158887367957
>>> print(a.to_bytes(32, sys.byteorder).hex())
1525616125251525610015000000000000000000000000000000000000000000
```
Which yields the states. The result is hashed and used as a key for an RC4 decryption. A new map is decrypted and loaded, where the flag is visible
