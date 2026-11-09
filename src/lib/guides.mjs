// Long-form buying guides for tool category pages.
// Renders inside /tools/<slug> under the comparison grid (see tools/[slug].astro).
// Voice rules: first person, exact numbers, short sentences, no em dashes, no AI words.

export const guides = {
  "torque-wrench": `
<h2>How to pick a torque wrench that still reads true next year</h2>
<p>A torque wrench does not measure tightness. It measures stretch. Every bolt is a spring, and the clamp load that holds your wheel or your head gasket comes from how far that spring gets pulled. Get it wrong in either direction and the failure stays quiet until it gets expensive.</p>

<h3>Start with the spec, then buy to the middle of the range</h3>
<p>Factory numbers decide everything. Passenger car lug nuts usually land between 80 and 100 ft-lb. Heavy-duty trucks run 145 to 250 ft-lb, and a Ford F-250 or F-350 sits near 165 to 180 ft-lb. Your owner's manual has the exact figure, and that is not a number to guess at.</p>
<p>Once you know the spec, buy a wrench whose middle covers it. A torque wrench is most accurate across the middle of its range, not at the very bottom or the very top.</p>
<p>1/4-inch drive covers roughly 20 to 200 in-lb. Bike stems, small engine covers, interior trim.<br/>
3/8-inch drive covers roughly 5 to 80 ft-lb. Valve covers, spark plugs, most 10mm to 15mm engine fasteners.<br/>
1/2-inch drive covers roughly 10 to 250 ft-lb. Lug nuts, suspension work, anything that fights back.</p>

<h3>Click, split-beam, or digital</h3>
<p>Click wrenches are the default for good reason. They hold about +/-4% accuracy when new, which is the tolerance most brands test to against the ISO 6789 standard, and you feel the break through the handle instead of watching a needle.</p>
<p>A split-beam wrench never goes out of adjustment because there is nothing to adjust. It just flexes against your setting. The trade off is the scale, which you read at an angle in a wheel well.</p>
<p>Digital wrenches earn their price in two places: tight engine bays where you cannot see a scale, and jobs where you have to torque the same bolt in stages. A digital unit beeps, vibrates, and holds the peak reading after you let go.</p>

<h3>The habit that kills accuracy</h3>
<p>Store a click wrench at its lowest setting. Leaving it parked at 100 ft-lb for a year is what puts a wrench out of spec, not normal use. Dial it back to the bottom of the range after every job and the calibration lasts for years.</p>
<p>Three more rules. Never use a torque wrench to break a fastener loose, because you will load it past its range in the wrong direction. Never put an impact gun on it. And never hang a cheater bar on the handle to reach a stuck bolt. Use a breaker bar for that, then come back with the torque wrench for the final pull.</p>

<h3>Do you need the $156 wrench?</h3>
<p>If you torque four wheels twice a year, no. A $20 to $55 click wrench in the right range does that job correctly, and the budget pick on this page has the lifetime warranty to back it.</p>
<p>Spend up when your work is internal. Head bolts, main bearings, and clutch assemblies punish a 5 ft-lb error, and a certified wrench with a NIST-traceable calibration sheet is worth the money the first time it saves an engine. The CDI on this page is the one I point engine builders to, because it is the same tool class the pros use without the truck brand markup.</p>

<h3>Tighten in a pattern, not in a circle</h3>
<p>Torque sequence matters as much as the number. Wheel lugs go in a star pattern across the hub, and the good practice is two passes: bring them all to half spec, then finish at full spec. Cylinder heads follow the factory sequence in the manual, usually inside out in stages. Skipping the pattern warps the part you just spent an hour torqueing perfectly.</p>

<h3>How often does a wrench need checking?</h3>
<p>Home use: once a year is plenty, and a cheap beam-type bar hanging next to it makes a free sanity check for the click type. Shop use: every six months, or any time the wrench gets dropped. A dropped torque wrench is a suspect wrench, and calibration services charge around $40 to $60 to confirm it either way.</p>

<h3>What about torque adapters and extensions?</h3>
<p>Straight extensions change nothing measurable at these values. What does change the reading is a crowfoot or a swivel placed at an angle. A crowfoot used at 90 degrees to the handle reads accurate. Used in line with the handle, it adds leverage and you have to do the math. If that sentence is confusing, the short version is: keep crowfeet at a right angle to the wrench and stop worrying about it.</p>
`,

  "air-compressor": `
<h2>Size a compressor by CFM, not by tank size</h2>
<p>The tank is a battery. The pump is the engine. CFM at 90 PSI tells you what the pump can actually deliver while a tool is running, and that is the number that decides whether your impact wrench hits with full power or stalls halfway through a lug nut.</p>

<h3>The CFM each tool pulls at 90 PSI</h3>
<p>1/2-inch impact wrench: 4 to 6 CFM.<br/>
Air ratchet: 3 to 5 CFM.<br/>
Die grinder: 5 to 10 CFM.<br/>
Blow gun: 2 to 4 CFM.<br/>
Tire inflator: about 2 CFM.</p>
<p>Compare that to this page's picks. The California Air Tools 10020C delivers 5.30 CFM at 90 PSI from a 10-gallon tank. The Makita Big Bore delivers 6.5 CFM. The Porter-Cable pancake delivers 2.6 CFM from a 6-gallon tank.</p>
<p>That gap explains everything. The pancake runs a nailer and tops off tires all day. Put a die grinder on it and the grinder starves. The tool slows down, the metal stops cutting, and you blame the tool instead of the 2.6 CFM feeding it.</p>

<h3>What the tank size actually buys you</h3>
<p>A bigger tank buys burst time. An impact wrench fires for two seconds at a time, so even a small tank keeps up, because the pump refills between bursts. A continuous tool like a sander or a die grinder never gives the pump that break, which is why continuous tools are where compressors get returned.</p>
<p>Rule of thumb: buy at least 1.5 times the CFM of the hungriest tool you own. If you only run an impact wrench at 5 CFM, a 7 CFM compressor never works hard. If you own a die grinder at 8 CFM, a 5 CFM unit will not do it, no matter how large the tank is.</p>

<h3>Oil-free or oil-lubed</h3>
<p>Oil-free pumps are cheaper, lighter, and need no maintenance beyond draining the tank. They also run hotter, sound worse, and usually carry a duty cycle around 50%, meaning five minutes of running for five minutes of rest.</p>
<p>Oil-lubed cast iron pumps run cooler, last longer in a shop, and are the only sensible choice if you plan to run air tools for twenty minutes straight. They cost more, weigh more, and need an oil change. The Makita on this page is that category, which is why it weighs 88 lbs.</p>

<h3>Noise is a spec, not a footnote</h3>
<p>You can talk over a 70 dB compressor. You shout over an 85 dB one. Every 10 dB is roughly a doubling of perceived loudness, so 88 dB is not "a bit louder" than 70 dB, it is four times louder by ear. If the compressor lives in a garage attached to the house, pay for the quiet unit. The California Air Tools at 70 dB and the Stealth at 68 dB exist for exactly that reason.</p>

<h3>Volts, amps, and the garage circuit</h3>
<p>Most home garages run 15A at 120V on a shared circuit. A 2 HP compressor pulls around 15A on startup, which is why a garage compressor tripping the breaker is so common. If you buy a 3 HP class unit, plan on a dedicated 20A circuit, or run it on 240V where the amperage draw drops by half.</p>

<h3>Water is the quiet killer</h3>
<p>Compressed air carries moisture, and moisture ruins paint jobs, rusts tools, and destroys a cheap impact wrench from the inside. Drain the tank after every session through the bottom valve. Add an inline filter and regulator at the outlet. Nothing on this page will last if it sits full of condensation.</p>

<h3>Portable 12V units solve a different problem</h3>
<p>A VIAIR-style portable is not a garage compressor and should not be judged like one. Its rating is 2.30 CFM at 0 PSI with a 33% duty cycle at 100 PSI, which is honest language for "it fills tires slowly and then needs to cool." For a truck tire on the side of the road, that is the tool you want. For a die grinder, it is the wrong tool entirely.</p>
`,

  "socket-set": `
<h2>Drive size, point count, and the sockets you will actually use</h2>
<p>Most socket sets fail at the same place. Not quality, but composition. You get 200 pieces, and 120 of them are sizes you will never touch while the one you need every week is missing.</p>

<h3>The three drive sizes and what they are for</h3>
<p>1/4-inch drive handles small fasteners, roughly 5mm through 14mm. Interior trim, dash work, hose clamps, anything where a 3/8-inch ratchet will not fit.</p>
<p>3/8-inch drive is the workhorse. It reaches most engine bay fasteners from 8mm to 19mm, and it is the size you will pick up nine times out of ten.</p>
<p>1/2-inch drive is for the fasteners that fight. Lug nuts, suspension bolts, brake caliper brackets, and anything over 19mm. You need the leverage, and you need sockets that will not split under it.</p>
<p>A set that skips 1/4-inch drive entirely is a set you will supplement within a month. The GEARWRENCH 110-piece set on this page covers all three drives in one case, which is exactly why it is the top pick.</p>

<h3>6-point versus 12-point</h3>
<p>A 6-point socket grips six flats. A 12-point grips twelve corners. More contact on the flats means a 6-point socket rounds fewer bolt heads, especially on anything rusted or already chewed up.</p>
<p>So why do 12-point sockets exist? Swing arc. In a tight spot where you cannot move the ratchet far, a 12-point lets you re-engage in 30 degrees instead of 60. That is the whole advantage, and it is a real one on old engine castings.</p>
<p>Practical answer: reach for 6-point first, keep 12-point for clearance. A quality set includes both, and this page's picks do.</p>

<h3>Chrome vanadium versus impact sockets</h3>
<p>Hand sockets are typically chrome vanadium. They are hard, shiny, and thin-walled so they fit in tight places.</p>
<p>Impact sockets are chrome molybdenum. They are slightly softer and noticeably thicker, and that is deliberate. When an impact wrench hammers a fastener, a hard socket can crack. A softer socket absorbs that shock instead of shattering.</p>
<p>Never put a chrome hand socket on an impact wrench. Not once. This is the single most common way people turn a $5 socket into shrapnel, and the impact socket set review linked on this page covers the dedicated sets that survive it.</p>

<h3>Deep, shallow, and the pieces nobody mentions</h3>
<p>Shallow sockets are for most work. Deep sockets earn their space for nuts on long studs, spark plugs, and anything where the fastener sits below a surface.</p>
<p>Two accessories separate a usable kit from an annoying one. Extensions in 3, 6, and 10 inches, because the right length is the difference between a 20-second job and a knuckle injury. A universal joint or two, for the fasteners that are simply not in line with your hand.</p>

<h3>The piece-count trap</h3>
<p>Big numbers sell. Look at what the count is made of. A "200-piece" set that includes 80 driver bits, 20 hex keys, and three magnetic trays has fewer real sockets than a focused 110-piece set.</p>
<p>Read the size list before you buy. You want no skipped sizes across 8mm to 19mm in 3/8-inch drive, a deep set in the common sizes, and both SAE and metric if you touch anything American.</p>

<h3>Why the 10mm goes missing</h3>
<p>Every mechanic loses them, and the reason is boring: 10mm is the most common fastener size on modern cars, so it gets used ten times more often than anything else and gets set down somewhere. Buy a spare 10mm before you need it. A set that comes with two is a set made by someone who has done this before.</p>

<h3>Ratchet tooth count matters more than you think</h3>
<p>A 72-tooth ratchet needs 5 degrees of swing to click. A 36-tooth needs 10. Under a dash or beside a shock tower, that difference decides whether the job takes one hand and a minute, or two hands and swearing. The 110-piece and 192-piece sets on this page both run 72-tooth ratchets.</p>
`,
};
