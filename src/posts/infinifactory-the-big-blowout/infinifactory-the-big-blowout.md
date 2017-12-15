Title:        Infinifactory: The Big Blowout
Author:       Etienne Perot <etienne (at) perot (dot) me>
Date:         2017-12-14
License:      CC-BY-3.0
ThumbnailUrl: thumb-screenshot.png

*This is an image-heavy post.*

I love [Zachtronics]. One of their games is [Infinifactory] ([Trailer][Infinifactory trailer]), a 3D puzzle game where you assemble blocks to form a certain product.

One of the later levels of the game is called "The Big Blowout" (Resistance Campaign → The Heist → The Big Blowout) in which you assemble a bomb-like device that looks like a hollow cube. It's quite difficult to assemble.

I had stopped playing it a while ago, but someone in my Steam friend list recently asked me to see my solution for this puzzle, so I recorded some GIFs using the game's built-in GIF recording feature. This made me re-discover the solution and I thought it was pretty cool so I'm posting it as a blog post.

**Solution stats: 327 cycles, 309 footprint, 386 blocks.** This is not the best. Here's [someone smarter than me doing it in 276 cycles][Better solution].

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Final product

The final product appears to be a bomb-like cube. It is hollow in the middle and all 4 sides have a hollow center with grey edges. The top and bottom are all black blocks with an orange center.

[![Product cube thumbnail][]][Product cube]

## Overall structure

The level is made of 2 stages linked by a single-block (purple) teleporter.
This is the largest limiting factor of the level. You cannot transfer more than one block per cycle through the teleporter. Thus, **the main factor that determines the solution's speed is how highly utilized the teleporter cube is**, i.e. the percentage of cycles during which the solution is using the teleporter cube to teleport a block.

To this end, the solution tries to build a single long chain of blocks that correspond to exactly one unit of the final product, then pushes this chain all at once through the teleporter. Because all the blocks are aligned in a chain, no cycle is wasted from block to block. **While the chain is being pushed, the next chain is being assembled right above the chain being pushed**. Once the first chain is fully through the teleporter block, the next chain is done assembling and falls right into the conveyor belt which pushes it through the teleporter, etc.

The other side of the teleporter is not very surprising. A redistributor first first lines up all the blocks from the chain in the same form as they arrived in through the teleporter. Once the chain is fully teleported, all blocks at pushed aside simultaneously in order to immediately make room for the next chain coming in through the teleporter. From there, the pushed-aside blocks get split up into multiple assembly lines that progressively weld them together until the final product is produced.

## Big picture

Here's an overall view of the solution.

Initial extraction & teleporter chain:

[![Big picture 1 thumbnail][]][Big picture 1]

Redistributor on the other side of the teleporter:

[![Big picture 2 thumbnail][]][Big picture 2]

Re-assembly lines:

[![Big picture 3 thumbnail][]][Big picture 3]

## Details

### Initial resource extraction

This section extracts the cubes from the dispending containers at the beginning of the level. It tries to be a non-blocking as possible, which is necessary in order to sustain enough extraction throughput to be able to build a new chain of material by the time the previous one is fully teleported. The main challenge are the black blocks (because the final product requires a lot of them), so the chain-building happens alongside the same line as the one directly taken by the black block dispending container.

[![Initial resource extraction 1 thumbnail][]][Initial resource extraction 1]

[![Initial resource extraction 2 thumbnail][]][Initial resource extraction 2]

[![Initial resource extraction 3 thumbnail][]][Initial resource extraction 3]

[![Initial resource extraction 4 thumbnail][]][Initial resource extraction 4]

### Teleporting the chain

This section buffers a chain of one product's worth of materials, then pushes it into the teleporter cube while buffering materials for the next chain.

[![Main chain 1 thumbnail][]][Main chain 1]

[![Main chain 2 thumbnail][]][Main chain 2]

### Redistributor

This section receives the chain from the teleporter. Once it is fully received, it pushes all blocks aside simultaneously to make room for the next chain to arrive. Blocks are grouped and move into distinct assembly lines.

[![Redistributor 1 thumbnail][]][Redistributor 1]

[![Redistributor 2 thumbnail][]][Redistributor 2]

### Lower conveyor

This section assembles the lower layer of the final product.

[![Lower conveyor thumbnail][]][Lower conveyor]

### Middle conveyor

This section assembles the middle layer of the final product, and brings extra black blocks to both the upper and the lower conveyors.

[![Middle conveyor 1 thumbnail][]][Middle conveyor 1]

[![Middle conveyor 2 thumbnail][]][Middle conveyor 2]

### Upper conveyor

This section assembles the top layer of the final product.

[![Upper conveyor thumbnail][]][Upper conveyor]

### Putting it all together

The middle conveyor drops the grey blocks onto the bottom conveyor to build the first 2 layers of the final product:

[![All together 1 thumbnail][]][All together 1]

Once assembled, the resulting partial product is brought back upwards to be on the same height as the product receptacle:

[![All together 2 thumbnail][]][All together 2]

The top conveyor drops the components of the top layer onto the partial product.

[![All together 3 thumbnail][]][All together 3]

[![All together 4 thumbnail][]][All together 4]

Finally, the finished product is conveyed to the product receptacle.

[![All together 5 thumbnail][]][All together 5]

## Bonus

Since you're still here, here are a few mesmerizing GIFs from Zachtronics's latest game, [Opus Magnum].

[![Opus Magnum Armor Filament thumbnail][]][Opus Magnum Armor Filament]

[![Opus Magnum Invisible Ink thumbnail][]][Opus Magnum Invisible Ink]

[![Opus Magnum Stain Remover thumbnail][]][Opus Magnum Stain Remover]

[![Opus Magnum Sword Alloy thumbnail][]][Opus Magnum Sword Alloy]

[![Opus Magnum Universal Solvent thumbnail][]][Opus Magnum Universal Solvent]

[![Opus Magnum Very Dark Thread thumbnail][]][Opus Magnum Very Dark Thread]

[![Opus Magnum Unstable Compound thumbnail][]][Opus Magnum Unstable Compound]

[![Opus Magnum Purified Gold thumbnail][]][Opus Magnum Purified Gold]

## Conclusion

I am not affiliated with Zachtronics, I just love their games. You should buy them. They are all available DRM-free on [Steam][Zachtronics on Steam] and [GOG][Zachtronics on GOG] for reasonable prices and they all work on Linux.

[Zachtronics]: http://www.zachtronics.com/
[Infinifactory]: http://www.zachtronics.com/infinifactory/
[Infinifactory trailer]: https://www.youtube.com/watch?v=kgnRTimOYGk
[Better solution]: https://www.youtube.com/watch?v=Gd0kpAzowr4
[Opus Magnum]: http://www.zachtronics.com/opus-magnum/
[Zachtronics on Steam]: https://store.steampowered.com/search/?developer=Zachtronics
[Zachtronics on GOG]: https://www.gog.com/games?devpub=zachtronics

[Product cube]: product-cube.png
[Product cube thumbnail]: product-cube-thumbnail.png
[Big picture 1]: big-picture-1.gif
[Big picture 1 thumbnail]: big-picture-1-thumbnail.gif
[Big picture 2]: big-picture-2.gif
[Big picture 2 thumbnail]: big-picture-2-thumbnail.gif
[Big picture 3]: big-picture-3.gif
[Big picture 3 thumbnail]: big-picture-3-thumbnail.gif
[Initial resource extraction 1]: initial-resource-extraction-1.gif
[Initial resource extraction 1 thumbnail]: initial-resource-extraction-1-thumbnail.gif
[Initial resource extraction 2]: initial-resource-extraction-2.gif
[Initial resource extraction 2 thumbnail]: initial-resource-extraction-2-thumbnail.gif
[Initial resource extraction 3]: initial-resource-extraction-3.gif
[Initial resource extraction 3 thumbnail]: initial-resource-extraction-3-thumbnail.gif
[Initial resource extraction 4]: initial-resource-extraction-4.gif
[Initial resource extraction 4 thumbnail]: initial-resource-extraction-4-thumbnail.gif
[Main chain 1]: main-chain-1.gif
[Main chain 1 thumbnail]: main-chain-1-thumbnail.gif
[Main chain 2]: main-chain-2.gif
[Main chain 2 thumbnail]: main-chain-2-thumbnail.gif
[Redistributor 1]: redistributor-1.gif
[Redistributor 1 thumbnail]: redistributor-1-thumbnail.gif
[Redistributor 2]: redistributor-2.gif
[Redistributor 2 thumbnail]: redistributor-2-thumbnail.gif
[Lower conveyor]: lower-conveyor.gif
[Lower conveyor thumbnail]: lower-conveyor-thumbnail.gif
[Middle conveyor 1]: middle-conveyor-1.gif
[Middle conveyor 1 thumbnail]: middle-conveyor-1-thumbnail.gif
[Middle conveyor 2]: middle-conveyor-2.gif
[Middle conveyor 2 thumbnail]: middle-conveyor-2-thumbnail.gif
[Upper conveyor]: upper-conveyor.gif
[Upper conveyor thumbnail]: upper-conveyor-thumbnail.gif
[All together 1]: all-together-1.gif
[All together 1 thumbnail]: all-together-1-thumbnail.gif
[All together 2]: all-together-2.gif
[All together 2 thumbnail]: all-together-2-thumbnail.gif
[All together 3]: all-together-3.gif
[All together 3 thumbnail]: all-together-3-thumbnail.gif
[All together 4]: all-together-4.gif
[All together 4 thumbnail]: all-together-4-thumbnail.gif
[All together 5]: all-together-5.gif
[All together 5 thumbnail]: all-together-5-thumbnail.gif
[Opus Magnum Armor Filament]: opus-magnum-armor-filament.gif
[Opus Magnum Armor Filament thumbnail]: opus-magnum-armor-filament-thumbnail.gif
[Opus Magnum Invisible Ink]: opus-magnum-invisible-ink.gif
[Opus Magnum Invisible Ink thumbnail]: opus-magnum-invisible-ink-thumbnail.gif
[Opus Magnum Stain Remover]: opus-magnum-stain-remover.gif
[Opus Magnum Stain Remover thumbnail]: opus-magnum-stain-remover-thumbnail.gif
[Opus Magnum Sword Alloy]: opus-magnum-sword-alloy.gif
[Opus Magnum Sword Alloy thumbnail]: opus-magnum-sword-alloy-thumbnail.gif
[Opus Magnum Universal Solvent]: opus-magnum-universal-solvent.gif
[Opus Magnum Universal Solvent thumbnail]: opus-magnum-universal-solvent-thumbnail.gif
[Opus Magnum Very Dark Thread]: opus-magnum-very-dark-thread.gif
[Opus Magnum Very Dark Thread thumbnail]: opus-magnum-very-dark-thread-thumbnail.gif
[Opus Magnum Unstable Compound]: opus-magnum-unstable-compound.gif
[Opus Magnum Unstable Compound thumbnail]: opus-magnum-unstable-compound-thumbnail.gif
[Opus Magnum Purified Gold]: opus-magnum-purified-gold.gif
[Opus Magnum Purified Gold thumbnail]: opus-magnum-purified-gold-thumbnail.gif
