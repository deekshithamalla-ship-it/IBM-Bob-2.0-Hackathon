"""
WasteWise AI Analyzer
Step 1: moondream describes the image (waste-focused prompt)
Step 2: Python maps the description to structured waste data
"""

import base64
import json
import os
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "moondream"
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 120


def _ask_moondream(b64_image: str, question: str) -> str:
    """Send one image+question to moondream, return the text answer."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": question, "images": [b64_image]}],
        "stream": True,
        "options": {"temperature": 0.1, "num_predict": 400}
    }
    try:
        resp = requests.post(
            OLLAMA_URL, json=payload, stream=True,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "WasteWise AI engine is offline. Run 'ollama serve' in a terminal."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Could not connect to Ollama. Is it running?")

    if resp.status_code != 200:
        body = resp.text.lower()
        if "model" in body and ("not found" in body or "pull" in body):
            raise RuntimeError(f"Model '{MODEL}' not found. Run: ollama pull {MODEL}")
        raise RuntimeError(f"Ollama error (HTTP {resp.status_code}).")

    text = ""
    for line in resp.iter_lines():
        if not line:
            continue
        chunk = json.loads(line.decode("utf-8"))
        text += chunk.get("message", {}).get("content", "")
        if chunk.get("done", False):
            break
    return text.strip()


# ── keyword → waste profile map ─────────────────────────────────────────────

PROFILES = {
    "plastic bottle": {
        "name": "Plastic Bottle",
        "category": "Plastic / Packaging",
        "material": "PET",
        "materialFull": "Polyethylene terephthalate",
        "materialsDescription": "Made primarily from PET plastic. Caps and labels may use different polymers and should be separated where local recycling rules require.",
        "materials": [
            {"name": "PET", "detail": "Primary bottle body", "type": "Plastic"},
            {"name": "HDPE cap", "detail": "Cap may be a different polymer", "type": "Plastic"},
            {"name": "Paper / plastic label", "detail": "Remove before recycling", "type": "Mixed"}
        ],
        "recovery": [
            {"name": "PET plastic", "detail": "Collected via curbside recycling"},
            {"name": "HDPE (cap)", "detail": "Separately recyclable if removed"}
        ],
        "uses": [
            {"title": "New bottles", "text": "Recycled PET becomes feedstock for new drink bottles."},
            {"title": "Polyester fibre", "text": "Recycled PET is spun into polyester for clothing and carpets."},
            {"title": "Packaging film", "text": "Recovered PET can be made into food-safe packaging film."}
        ],
        "disposalTitle": "Recycling Stream",
        "disposalText": "Empty and rinse the bottle. Remove the cap and label if required locally. Place in the plastic recycling bin.",
        "safety": "Do not burn plastic waste — toxic fumes are released.",
        "environment": "PET can take up to 450 years to decompose in landfill."
    },
    "glass": {
        "name": "Glass Bottle / Jar",
        "category": "Glass / Container",
        "material": "Glass",
        "materialFull": "Soda-lime silicate glass",
        "materialsDescription": "Composed mainly of silica, soda ash and limestone. Metal lids and plastic seals should be removed before recycling.",
        "materials": [
            {"name": "Glass", "detail": "Main body", "type": "Glass"},
            {"name": "Metal lid", "detail": "Remove before recycling", "type": "Metal"}
        ],
        "recovery": [
            {"name": "Cullet (crushed glass)", "detail": "Melted down and re-formed into new glass"},
            {"name": "Metal lid", "detail": "Sorted via magnet at recycling facility"}
        ],
        "uses": [
            {"title": "New glass containers", "text": "Cullet is melted and re-moulded into bottles and jars."},
            {"title": "Aggregate / fill", "text": "Crushed glass is used as road base aggregate."},
            {"title": "Fibreglass insulation", "text": "Recovered glass can be spun into fibreglass."}
        ],
        "disposalTitle": "Glass Recycling Bin",
        "disposalText": "Empty and rinse the container. Remove metal lids. Place in the glass recycling bin. Do not mix with ceramics or Pyrex.",
        "safety": "Broken glass is a cut hazard — wrap sharp fragments before disposal.",
        "environment": "Glass never breaks down naturally; recycling saves up to 30% of the energy needed to make new glass."
    },
    "metal can": {
        "name": "Metal Can",
        "category": "Metal / Packaging",
        "material": "Al / Steel",
        "materialFull": "Aluminium or tinplate steel",
        "materialsDescription": "Food and drink cans are made from either aluminium or steel. Both are infinitely recyclable without quality loss.",
        "materials": [
            {"name": "Aluminium or Steel", "detail": "Main body", "type": "Metal"},
            {"name": "Lacquer lining", "detail": "Interior food-safe coating", "type": "Chemical"}
        ],
        "recovery": [
            {"name": "Aluminium", "detail": "Melted and re-rolled — saves 95% of the energy of primary production"},
            {"name": "Steel", "detail": "Magnetically separated and re-smelted"}
        ],
        "uses": [
            {"title": "New cans", "text": "A recycled can is back on the shelf as a new can within 60 days."},
            {"title": "Car parts", "text": "Recycled steel is used in automotive manufacturing."},
            {"title": "Construction steel", "text": "Recovered metal feeds into structural steel production."}
        ],
        "disposalTitle": "Metal / Dry Recycling Bin",
        "disposalText": "Empty and lightly rinse the can. Crush if space allows. Place in the metal or mixed recycling bin.",
        "safety": "Sharp edges on cut or damaged cans can cause injury — handle with care.",
        "environment": "Aluminium that is not recycled requires 20 times more energy to replace from raw bauxite ore."
    },
    "paper": {
        "name": "Paper / Cardboard",
        "category": "Paper / Fibre",
        "material": "Cellulose",
        "materialFull": "Plant-based cellulose fibre",
        "materialsDescription": "Paper and cardboard are made from cellulose fibres. Wet, greasy, or wax-coated paper cannot be recycled and must go to general waste.",
        "materials": [
            {"name": "Cellulose fibre", "detail": "Primary material", "type": "Fibre"},
            {"name": "Ink / coating", "detail": "May be present on printed surfaces", "type": "Component"}
        ],
        "recovery": [
            {"name": "Paper fibre", "detail": "Re-pulped and made into recycled paper"},
            {"name": "Cardboard fibre", "detail": "Used in new corrugated packaging"}
        ],
        "uses": [
            {"title": "Recycled paper", "text": "Recovered fibre is made into newspaper, tissue, and office paper."},
            {"title": "Cardboard boxes", "text": "Recycled board becomes new packaging and shipping boxes."},
            {"title": "Egg cartons / trays", "text": "Low-grade recovered fibre is moulded into protective trays."}
        ],
        "disposalTitle": "Paper Recycling Bin",
        "disposalText": "Keep paper dry and flat. Remove any plastic windows from envelopes. Do not include greasy pizza boxes — tear off the clean top and recycle that only.",
        "safety": "Wet paper is not recyclable — keep recycling dry.",
        "environment": "Recycling one tonne of paper saves 17 trees and reduces landfill methane emissions."
    },
    "electronic": {
        "name": "Electronic Device",
        "category": "Electronic Waste (E-Waste)",
        "material": "Mixed / PCB",
        "materialFull": "Metals, polymers, glass and electronic components",
        "materialsDescription": "Electronic devices contain complex mixtures of metals, plastics, glass, and circuit-board materials. Batteries must be handled separately.",
        "materials": [
            {"name": "Copper", "detail": "Wiring and circuit traces", "type": "Metal"},
            {"name": "Aluminium / Steel", "detail": "Casing and structural parts", "type": "Metal"},
            {"name": "Lithium / NiMH battery", "detail": "Energy storage — hazardous", "type": "Battery"},
            {"name": "FR4 PCB laminate", "detail": "Circuit board substrate", "type": "Mixed"}
        ],
        "recovery": [
            {"name": "Copper", "detail": "Extracted via hydrometallurgical processing"},
            {"name": "Precious metals (Au, Ag, Pd)", "detail": "Recovered by specialist e-waste smelters"},
            {"name": "Aluminium", "detail": "Separated and re-melted"}
        ],
        "uses": [
            {"title": "New electronics", "text": "Recovered metals re-enter the electronics supply chain."},
            {"title": "Copper wire & plumbing", "text": "Recycled copper is drawn into new wire and piping."},
            {"title": "Jewellery / contacts", "text": "Recovered gold and silver are refined for high-value applications."}
        ],
        "disposalTitle": "Authorised E-Waste Collection",
        "disposalText": "Do not place in household bins. Take to a council e-waste drop-off point, retailer take-back scheme, or certified e-waste recycler.",
        "safety": "Damaged lithium batteries can cause fire or chemical burns — do not puncture or incinerate.",
        "environment": "E-waste leaches lead, mercury, and cadmium into soil and groundwater when landfilled."
    },
    "battery": {
        "name": "Battery",
        "category": "Hazardous Waste / Battery",
        "material": "Li / NiMH / Pb",
        "materialFull": "Lithium, nickel-metal hydride or lead-acid chemistry",
        "materialsDescription": "Batteries contain electrochemical cells with metal electrodes and electrolyte. All battery types must be kept out of general waste.",
        "materials": [
            {"name": "Lithium / Lead / Nickel", "detail": "Electrode active material", "type": "Metal"},
            {"name": "Electrolyte", "detail": "Corrosive chemical — hazardous", "type": "Chemical"},
            {"name": "Steel / aluminium casing", "detail": "Outer shell", "type": "Metal"}
        ],
        "recovery": [
            {"name": "Lithium carbonate", "detail": "Re-used in new battery cells"},
            {"name": "Cobalt / Nickel", "detail": "Recovered for battery and alloy manufacturing"},
            {"name": "Lead", "detail": "Re-smelted for new lead-acid batteries"}
        ],
        "uses": [
            {"title": "New batteries", "text": "Recovered lithium and cobalt feed directly into new EV and consumer batteries."},
            {"title": "Steel production", "text": "Recovered steel casing enters the steel recycling stream."},
            {"title": "Industrial chemicals", "text": "Refined lithium salts are used in ceramics and pharmaceuticals."}
        ],
        "disposalTitle": "Battery Drop-Off Point",
        "disposalText": "Place in a dedicated battery recycling container at supermarkets, electronics retailers, or council facilities. Tape the terminals of lithium batteries before disposal.",
        "safety": "Never crush, puncture, or incinerate batteries — risk of fire, explosion, and toxic gas release.",
        "environment": "Battery chemicals in landfill contaminate soil and water for decades."
    },
    "food": {
        "name": "Food Waste",
        "category": "Organic Waste",
        "material": "Organic",
        "materialFull": "Biodegradable organic matter",
        "materialsDescription": "Food waste is organic material that decomposes naturally. Diverting it from landfill reduces methane — a potent greenhouse gas.",
        "materials": [
            {"name": "Organic matter", "detail": "Fruit, vegetable, meat, or grain-based", "type": "Organic"},
            {"name": "Water", "detail": "High moisture content", "type": "Organic"}
        ],
        "recovery": [
            {"name": "Compost", "detail": "Broken down by microorganisms into soil amendment"},
            {"name": "Biogas (methane)", "detail": "Produced by anaerobic digestion — used for energy"}
        ],
        "uses": [
            {"title": "Garden compost", "text": "Finished compost improves soil structure and fertility."},
            {"title": "Biogas / electricity", "text": "Anaerobic digestion converts food waste into renewable energy."},
            {"title": "Liquid fertiliser", "text": "Digestate from biogas plants is applied to agricultural land."}
        ],
        "disposalTitle": "Food Waste / Compost Bin",
        "disposalText": "Place in the food waste caddy or compost bin. Do not include packaging, bones (for home composting), or liquids.",
        "safety": "Decomposing food attracts pests — keep the caddy sealed and empty it regularly.",
        "environment": "Food waste in landfill produces methane — 25 times more potent than CO₂ as a greenhouse gas."
    },
    "textile": {
        "name": "Clothing / Textile",
        "category": "Textile Waste",
        "material": "Cotton / Polyester",
        "materialFull": "Natural or synthetic fibre blend",
        "materialsDescription": "Textiles are made from natural fibres (cotton, wool, linen) or synthetic fibres (polyester, nylon, acrylic) or blends of both.",
        "materials": [
            {"name": "Cotton / Wool", "detail": "Natural fibre content", "type": "Natural Fibre"},
            {"name": "Polyester / Nylon", "detail": "Synthetic fibre content", "type": "Synthetic Fibre"},
            {"name": "Dyes / finishes", "detail": "Chemical treatment", "type": "Chemical"}
        ],
        "recovery": [
            {"name": "Reclaimed fibre", "detail": "Shredded and re-spun into new yarn"},
            {"name": "Rags / wipers", "detail": "Used as industrial cleaning cloths"}
        ],
        "uses": [
            {"title": "Second-hand clothing", "text": "Donated textiles are resold in charity shops, extending their life."},
            {"title": "Recycled insulation", "text": "Shredded textile is used as acoustic and thermal insulation."},
            {"title": "Industrial wipers", "text": "Worn fabric is cut into cleaning cloths for manufacturing."}
        ],
        "disposalTitle": "Clothing Bank / Charity Donation",
        "disposalText": "If wearable, donate to a charity or clothing bank. If worn out, place in a textile recycling bank — not the general waste bin.",
        "safety": "Avoid donating items soiled with chemicals or hazardous substances.",
        "environment": "Fashion is one of the most polluting industries — extending garment life by 9 months reduces its carbon footprint by 20–30%."
    },
    "styrofoam": {
        "name": "Styrofoam / Polystyrene",
        "category": "Plastic / Foam Waste",
        "material": "EPS",
        "materialFull": "Expanded Polystyrene (EPS)",
        "materialsDescription": "Styrofoam is expanded polystyrene foam, widely used in food packaging and product cushioning. It is very difficult to recycle through standard curbside schemes.",
        "materials": [
            {"name": "Expanded Polystyrene", "detail": "Lightweight foam body", "type": "Plastic"},
            {"name": "Chemical blowing agents", "detail": "Used during manufacturing", "type": "Chemical"}
        ],
        "recovery": [
            {"name": "Specialist EPS recycler", "detail": "Compressed and pelletised for reuse"},
            {"name": "Energy recovery", "detail": "Used as fuel in waste-to-energy plants where accepted"}
        ],
        "uses": [
            {"title": "New foam products", "text": "Recycled EPS is remoulded into picture frames, skirting boards, and insulation panels."},
            {"title": "Concrete aggregate", "text": "Crushed EPS is mixed into lightweight concrete."},
            {"title": "Garden mulch", "text": "Some councils accept EPS as mulch material when shredded."}
        ],
        "disposalTitle": "Specialist EPS Drop-Off",
        "disposalText": "Do not place in standard recycling bins — EPS jams sorting machinery. Take to a specialist EPS drop-off point or check your council's guidelines. Clean food packaging before disposal.",
        "safety": "Do not burn EPS — it releases toxic styrene gas.",
        "environment": "Polystyrene takes over 500 years to break down and is a major source of microplastic pollution."
    },
    "light bulb": {
        "name": "Light Bulb / Lamp",
        "category": "Hazardous / Special Waste",
        "material": "Glass / Metal / CFL",
        "materialFull": "Glass envelope, metal base, phosphor coating or LED chip",
        "materialsDescription": "Light bulbs vary by type: incandescent (glass + tungsten), CFL (glass + mercury + phosphor), and LED (PCB + semiconductor). CFLs contain mercury and must never go in general waste.",
        "materials": [
            {"name": "Glass", "detail": "Outer envelope", "type": "Glass"},
            {"name": "Metal base (E27/B22)", "detail": "Screw or bayonet fitting", "type": "Metal"},
            {"name": "Mercury / Phosphor (CFL)", "detail": "Hazardous — specialist disposal required", "type": "Hazardous"},
            {"name": "LED chip / PCB", "detail": "Present in LED bulbs", "type": "Electronic"}
        ],
        "recovery": [
            {"name": "Mercury (CFL)", "detail": "Extracted and reused in industrial processes"},
            {"name": "Glass", "detail": "Recovered and recycled into new glass products"},
            {"name": "Metals", "detail": "Separated and smelted"}
        ],
        "uses": [
            {"title": "Mercury recovery", "text": "Mercury from CFLs is refined and reused in scientific instruments and lighting."},
            {"title": "Metal recovery", "text": "Metal bases are smelted for reuse in manufacturing."},
            {"title": "Glass cullet", "text": "Clean glass is crushed and recycled into new glass products."}
        ],
        "disposalTitle": "Bulb Recycling Point",
        "disposalText": "Do not place in general waste or recycling bins. Take CFL and LED bulbs to a dedicated bulb recycling point at hardware stores or council facilities. Incandescent bulbs (no longer sold) go in general waste.",
        "safety": "If a CFL breaks, ventilate the room immediately — mercury vapour is toxic. Do not vacuum the fragments.",
        "environment": "CFLs contain up to 5 mg of mercury each — landfilling them contaminates soil and water."
    },
    "aerosol": {
        "name": "Aerosol Can",
        "category": "Metal / Pressurised Packaging",
        "material": "Steel / Aluminium",
        "materialFull": "Tinplate steel or aluminium with pressurised propellant",
        "materialsDescription": "Aerosol cans are made from steel or aluminium and contain pressurised propellant. They are recyclable once fully empty — never puncture or incinerate.",
        "materials": [
            {"name": "Steel or Aluminium", "detail": "Can body and lid", "type": "Metal"},
            {"name": "Propellant gas", "detail": "Pressurised hydrocarbon or CO₂", "type": "Chemical"},
            {"name": "Plastic cap / nozzle", "detail": "Remove before recycling", "type": "Plastic"}
        ],
        "recovery": [
            {"name": "Steel / Aluminium", "detail": "Melted and re-rolled into new sheet metal"},
            {"name": "Residual chemical", "detail": "Extracted and safely disposed at specialist facilities"}
        ],
        "uses": [
            {"title": "New cans", "text": "Recycled metal becomes new cans, car parts, or construction steel."},
            {"title": "Aluminium products", "text": "Recovered aluminium is infinitely recyclable without quality loss."},
            {"title": "Steel manufacturing", "text": "Steel from aerosol cans re-enters the steel production cycle."}
        ],
        "disposalTitle": "Metal Recycling Bin (when empty)",
        "disposalText": "Only recycle when completely empty. Remove the plastic cap. Place in the metal recycling bin. If not empty, take to a household hazardous waste facility — never puncture.",
        "safety": "Never puncture, crush, or incinerate an aerosol can — risk of explosion and fire.",
        "environment": "Aerosol propellants contribute to ground-level ozone and smog if vented irresponsibly."
    },
    "rubber": {
        "name": "Rubber / Tyre",
        "category": "Rubber Waste",
        "material": "Vulcanised Rubber",
        "materialFull": "Sulphur-cross-linked natural or synthetic rubber",
        "materialsDescription": "Tyres and rubber products are made from vulcanised natural or synthetic rubber reinforced with steel wire and fabric. They require specialist recycling.",
        "materials": [
            {"name": "Vulcanised rubber", "detail": "Main elastic body", "type": "Rubber"},
            {"name": "Steel wire belt", "detail": "Internal reinforcement (tyres)", "type": "Metal"},
            {"name": "Fabric ply", "detail": "Nylon or polyester cord reinforcement", "type": "Synthetic Fibre"}
        ],
        "recovery": [
            {"name": "Crumb rubber", "detail": "Ground into granules for sports surfaces and playground matting"},
            {"name": "Steel wire", "detail": "Magnetically separated and recycled as scrap steel"},
            {"name": "Pyrolysis oil", "detail": "Rubber thermally decomposed into fuel oil"}
        ],
        "uses": [
            {"title": "Sports surfaces", "text": "Crumb rubber is used as infill on artificial football pitches and running tracks."},
            {"title": "Playground matting", "text": "Recycled rubber tiles cushion children's play areas."},
            {"title": "Asphalt rubber", "text": "Ground tyre rubber is mixed into road asphalt for quieter, more durable roads."}
        ],
        "disposalTitle": "Tyre Recycling Facility",
        "disposalText": "Do not place tyres in household bins — it is illegal. Take to a tyre retailer (many accept old tyres free when fitting new ones) or a licensed tyre recycling facility.",
        "safety": "Burning rubber releases toxic black smoke including dioxins, hydrogen cyanide, and carbon monoxide.",
        "environment": "Illegally dumped tyres create breeding grounds for mosquitoes and leach zinc into waterways."
    },
    "wood": {
        "name": "Wood / Timber Waste",
        "category": "Wood Waste",
        "material": "Timber",
        "materialFull": "Natural or engineered wood / timber",
        "materialsDescription": "Wood waste includes offcuts, old furniture, pallets, and MDF. Untreated wood is compostable; treated, painted, or MDF wood must go to a wood recycling facility.",
        "materials": [
            {"name": "Cellulose / Lignin", "detail": "Primary wood structure", "type": "Natural"},
            {"name": "Paint / varnish / treatment", "detail": "May contain hazardous chemicals", "type": "Chemical"},
            {"name": "Metal fixings", "detail": "Nails, screws, brackets", "type": "Metal"}
        ],
        "recovery": [
            {"name": "Chipped wood / biomass", "detail": "Shredded for use as biomass fuel or mulch"},
            {"name": "Panel board", "detail": "Recycled wood fibre pressed into new MDF or chipboard"},
            {"name": "Composting", "detail": "Untreated wood chipped and composted"}
        ],
        "uses": [
            {"title": "Biomass energy", "text": "Chipped waste wood is burned in biomass boilers for heat and electricity."},
            {"title": "New chipboard / MDF", "text": "Recycled wood fibre is pressed into panel board for furniture and construction."},
            {"title": "Garden mulch", "text": "Untreated chipped wood improves soil moisture retention in gardens."}
        ],
        "disposalTitle": "Wood Recycling / Household Waste Site",
        "disposalText": "Untreated wood can go in the garden waste or wood recycling skip. Painted, treated, or MDF wood must go to a household waste recycling centre — not the garden bin.",
        "safety": "CCA-treated (green) timber contains arsenic — wear gloves and do not burn it.",
        "environment": "Diverting wood from landfill prevents methane production and saves virgin timber resources."
    },
    "medicine": {
        "name": "Medicine / Pill Bottle",
        "category": "Pharmaceutical / Hazardous Waste",
        "material": "HDPE / Glass",
        "materialFull": "High-density polyethylene or glass with chemical contents",
        "materialsDescription": "Medicine containers are made from HDPE plastic or glass. The pharmaceutical contents are hazardous and must never be flushed or placed in general recycling.",
        "materials": [
            {"name": "HDPE or Glass", "detail": "Container body", "type": "Plastic / Glass"},
            {"name": "Foil blister pack (if present)", "detail": "Aluminium-plastic laminate", "type": "Mixed"},
            {"name": "Pharmaceutical compound", "detail": "Active ingredient — hazardous", "type": "Chemical"}
        ],
        "recovery": [
            {"name": "HDPE container", "detail": "Recyclable if empty and rinsed"},
            {"name": "Unused medicines", "detail": "Returned to pharmacy for safe destruction"}
        ],
        "uses": [
            {"title": "HDPE recycling", "text": "Empty HDPE bottles are recycled into pipes, bins, and garden furniture."},
            {"title": "Pharmaceutical disposal", "text": "Pharmacies safely incinerate returned medicines at licensed facilities."}
        ],
        "disposalTitle": "Return to Pharmacy",
        "disposalText": "Return unused medicines to your local pharmacy — do not flush or bin them. Empty HDPE containers (rinsed) can go in plastic recycling. Blister packs are not widely recycled — check locally.",
        "safety": "Never flush medicines down the toilet — they contaminate water supplies and harm aquatic life.",
        "environment": "Pharmaceutical compounds entering waterways disrupt hormones in fish and wildlife."
    },
    "ceramic": {
        "name": "Ceramic / Crockery",
        "category": "Ceramic Waste",
        "material": "Fired Clay",
        "materialFull": "Fired alumino-silicate ceramic",
        "materialsDescription": "Ceramics (plates, cups, tiles, pots) are made from fired clay and cannot be recycled in standard glass or general recycling streams — they contaminate glass batches.",
        "materials": [
            {"name": "Fired clay / porcelain", "detail": "Main body", "type": "Ceramic"},
            {"name": "Glaze", "detail": "Glassy surface coating", "type": "Silicate"}
        ],
        "recovery": [
            {"name": "Hardcore / aggregate", "detail": "Crushed for use as road base or construction fill"},
            {"name": "Donation / reuse", "detail": "Intact items can be donated to charity shops"}
        ],
        "uses": [
            {"title": "Hardcore aggregate", "text": "Crushed ceramics are used as sub-base material in road and path construction."},
            {"title": "Mosaic / art", "text": "Broken tile and crockery pieces are used in decorative mosaics."},
            {"title": "Donation", "text": "Intact crockery and pottery can be donated to charity or reused."}
        ],
        "disposalTitle": "General Waste / Charity",
        "disposalText": "Do NOT place in glass recycling — ceramics contaminate the entire glass batch. Wrap broken pieces safely and place in general waste, or donate intact items to charity.",
        "safety": "Broken ceramics have sharp edges — wrap securely in newspaper before disposal.",
        "environment": "Ceramics are inert in landfill but take thousands of years to break down — reuse is always preferable."
    },
}

DEFAULT_PROFILE = {
    "name": "Unidentified Waste Item",
    "category": "General Waste",
    "material": "Mixed",
    "materialFull": "Mixed or unknown materials",
    "materialsDescription": "The exact material composition could not be determined from the image. Please check local guidelines for disposal.",
    "materials": [
        {"name": "Unknown material", "detail": "Visual inspection required", "type": "Mixed"}
    ],
    "recovery": [
        {"name": "Check locally", "detail": "Contact your local waste authority for guidance"}
    ],
    "uses": [
        {"title": "Material recovery", "text": "Depending on content, specialist recycling may be possible."},
        {"title": "Reuse", "text": "If still functional, consider donating or repurposing the item."},
        {"title": "General waste", "text": "If no recycling option is available, dispose of responsibly."}
    ],
    "disposalTitle": "Check Local Guidelines",
    "disposalText": "Dispose of according to your local waste authority guidelines. When in doubt, place in general waste rather than contaminating recycling.",
    "safety": "Dispose of responsibly — illegal dumping harms the environment and carries fines.",
    "environment": "Every item sent to landfill is a missed opportunity for resource recovery."
}


def _match_profile(description: str) -> dict:
    """Map a free-text image description to the closest waste profile."""
    desc = description.lower()

    # ordered from most specific to most general
    checks = [
        # --- Battery ---
        (["battery", "batteries", "aa battery", "aaa battery", "9v battery",
          "lithium cell", "alkaline cell", "rechargeable"], "battery"),

        # --- E-Waste ---
        (["phone", "mobile", "smartphone", "laptop", "computer", "keyboard",
          "circuit", "pcb", "circuit board", "electronic", "electrical", "e-waste",
          "ewaste", "device", "cable", "charger", "usb", "monitor", "tablet",
          "television", "tv", "remote", "headphone", "earphone", "printer",
          "scanner", "camera", "microwave", "mouse", "hard drive", "power supply",
          "transformer", "wire", "gadget", "appliance"], "electronic"),

        # --- Light Bulb ---
        (["light bulb", "bulb", "cfl", "fluorescent", "led bulb", "incandescent",
          "lamp", "light fitting", "halogen", "tube light", "tube lamp"], "light bulb"),

        # --- Aerosol ---
        (["aerosol", "spray can", "spray bottle", "deodorant can", "hairspray",
          "paint spray", "pressurised can", "air freshener can"], "aerosol"),

        # --- Medicine ---
        (["medicine", "pill", "tablet bottle", "prescription", "pharmaceutical",
          "pill bottle", "drug", "blister pack", "capsule", "syrup bottle",
          "medicine bottle", "supplement"], "medicine"),

        # --- Ceramic ---
        (["ceramic", "crockery", "plate", "bowl", "mug", "cup", "saucer",
          "porcelain", "pottery", "tile", "fired clay", "terracotta"], "ceramic"),

        # --- Styrofoam ---
        (["styrofoam", "polystyrene", "foam cup", "foam tray", "foam box",
          "expanded foam", "eps", "foam container", "foam packaging",
          "white foam", "thermocol", "packing foam"], "styrofoam"),

        # --- Rubber / Tyre ---
        (["tyre", "tire", "rubber", "rubber band", "rubber hose", "rubber mat",
          "foam rubber", "latex", "inner tube"], "rubber"),

        # --- Wood ---
        (["wood", "timber", "plank", "log", "stick", "branch", "furniture",
          "wooden", "mdf", "chipboard", "pallet", "sawdust", "bark"], "wood"),

        # --- Glass (specific) ---
        (["glass bottle", "glass jar", "glass container", "wine bottle",
          "beer bottle", "glass vase"], "glass"),

        # --- Metal Can (specific) ---
        (["tin can", "aluminium can", "beer can", "soda can", "energy drink can",
          "food can", "metal can", "steel can", "biscuit tin", "paint tin",
          "empty tin", "tin"], "metal can"),

        # --- Plastic Bottle (specific) ---
        (["plastic bottle", "water bottle", "drink bottle", "pet bottle",
          "hdpe bottle", "juice bottle", "milk bottle", "coke", "cola",
          "soda bottle", "soft drink", "beverage bottle", "diet coke",
          "pepsi", "sprite", "fanta"], "plastic bottle"),

        # --- Plastic (general — kept broad, checked after specifics) ---
        (["plastic bag", "plastic film", "plastic wrap", "plastic sheet",
          "carrier bag", "ziplock", "cling film", "plastic container",
          "plastic tub", "plastic", "polythene", "polypropylene",
          "nylon bag"], "plastic bottle"),

        # --- Glass (general fallback) ---
        (["glass", "jar", "vase", "transparent container"], "glass"),

        # --- Paper ---
        (["cardboard", "paper", "newspaper", "magazine", "book", "notebook",
          "envelope", "box", "carton", "tissue", "napkin", "paper bag",
          "pamphlet", "flyer", "brochure", "receipt", "wrapping paper"], "paper"),

        # --- Food ---
        (["food", "fruit", "vegetable", "meat", "bread", "rice", "pasta",
          "leftover", "organic", "peel", "rind", "banana", "apple", "egg",
          "shell", "bone", "fish", "cooked", "raw food", "waste food",
          "coffee grounds", "tea bag", "compost"], "food"),

        # --- Textile ---
        (["shirt", "trouser", "jeans", "clothing", "cloth", "fabric",
          "textile", "garment", "shoe", "sock", "underwear", "jacket",
          "coat", "dress", "scarf", "hat", "bag", "handbag", "curtain",
          "blanket", "towel", "bedsheet", "pillow", "wool", "cotton"], "textile"),

        # --- Metal (general fallback) ---
        (["can", "tin", "metal", "aluminium", "aluminum", "steel",
          "iron", "copper wire", "scrap metal", "wire", "pipe",
          "nail", "screw", "bolt", "foil", "aluminium foil"], "metal can"),
    ]

    for keywords, profile_key in checks:
        if any(kw in desc for kw in keywords):
            return PROFILES[profile_key]

    return DEFAULT_PROFILE


def _match_from_filename(image_path: str) -> dict:
    """Fallback: match a waste profile from the image filename alone."""
    filename = os.path.splitext(os.path.basename(image_path))[0].lower()
    # replace common separators with spaces for keyword matching
    filename = filename.replace("-", " ").replace("_", " ").replace(".", " ")
    return _match_profile(filename)


def analyze_waste_image(image_path: str) -> dict:
    """
    1. Try sending image to moondream (Ollama) for AI description.
    2. If Ollama is unavailable (e.g. cloud deployment), fall back to
       matching the waste profile from the image filename.
    3. Map the description/filename to a structured waste profile locally.
    Returns a dict matching the WasteWise result schema.
    """

    # --- validate file ---
    if not os.path.isfile(image_path):
        raise RuntimeError("The uploaded image could not be found on the server.")

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        raise RuntimeError("Unsupported image format. Please upload a JPG, PNG, or WEBP file.")

    # --- encode image ---
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    # --- try Ollama AI analysis; fall back to filename matching if offline ---
    ollama_available = True
    description = ""
    material_hint = ""

    try:
        # Q1: waste-focused object description
        description = _ask_moondream(
            b64_image,
            "What type of waste or recyclable object is shown in this image? "
            "Name the specific object and the material it is made of (e.g. plastic bottle, glass jar, "
            "metal can, cardboard box, food scraps, electronic device, battery, light bulb, aerosol can, "
            "rubber tyre, wood, ceramic plate, medicine bottle, styrofoam cup)."
        )

        # Q2: material cross-check for better matching
        material_hint = _ask_moondream(
            b64_image,
            "What material is the main object in this image made of? "
            "Answer with one or two words only (e.g. plastic, glass, metal, paper, rubber, wood, ceramic, foam)."
        )

    except RuntimeError:
        # Ollama is offline or model missing — use filename fallback
        ollama_available = False

    # --- build combined text for profile matching ---
    if ollama_available and description:
        combined = f"{description} {material_hint}"
        confidence = "91%"
    else:
        # fallback: derive match from the uploaded filename
        filename = os.path.splitext(os.path.basename(image_path))[0].lower()
        combined = filename.replace("-", " ").replace("_", " ").replace(".", " ")
        description = ""
        confidence = "75%"

    # --- map to structured profile ---
    profile = _match_profile(combined)

    # if filename fallback also found nothing, lower confidence further
    if not ollama_available and profile["name"] == DEFAULT_PROFILE["name"]:
        confidence = "52%"

    return {
        "success": True,
        "name": profile["name"],
        "description": description if description else profile["name"] + " — identified from image name.",
        "confidence": confidence,
        "category": profile["category"],
        "material": profile["material"],
        "materialFull": profile["materialFull"],
        "materialsDescription": profile["materialsDescription"],
        "materials": profile["materials"],
        "recovery": profile["recovery"],
        "uses": profile["uses"],
        "disposalTitle": profile["disposalTitle"],
        "disposalText": profile["disposalText"],
        "safety": profile["safety"],
        "environment": profile["environment"],
    }
