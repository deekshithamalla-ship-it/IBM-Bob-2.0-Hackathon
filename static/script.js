// ============================================================
// WASTEWISE - AI WASTE INTELLIGENCE
// ============================================================


// ================= ELEMENTS =================

const imageInput = document.getElementById("imageInput");

const uploadBox = document.getElementById("uploadBox");

const previewContainer =
    document.getElementById("previewContainer");

const previewImage =
    document.getElementById("previewImage");

const resultsContainer =
    document.getElementById("resultsContainer");

const progressBar =
    document.getElementById("progressBar");

const progressText =
    document.getElementById("progressText");

const scanMessage =
    document.getElementById("scanMessage");

const scanSubMessage =
    document.getElementById("scanSubMessage");


// ================= DEMO WASTE DATABASE =================
// This is temporary.
// Later this will be replaced with real AI output.

const wasteDatabase = {

    plastic: {

        name: "Plastic Bottle",

        description:
            "A commonly encountered plastic packaging item.",

        confidence: "94%",

        category:
            "Plastic / Packaging",

        material:
            "PET",

        materialFull:
            "Polyethylene terephthalate",

        materialsDescription:
            "The detected item is primarily associated with PET plastic. Other visible components such as caps and labels may use different materials and should be separated where local recycling systems require it.",

        materials: [
            {
                name: "PET",
                detail: "Primary material",
                type: "Plastic"
            },
            {
                name: "Cap / label",
                detail: "May contain different polymers",
                type: "Component"
            }
        ],

        recovery: [
            {
                name: "PET",
                detail: "Recycled plastic feedstock"
            },
            {
                name: "Plastic components",
                detail: "May be separately sorted"
            }
        ],

        uses: [
            {
                title: "New containers",
                text: "Recovered plastic can serve as feedstock for suitable new products."
            },
            {
                title: "Textile fibres",
                text: "Recycled PET can be processed into polyester fibre for textile applications."
            },
            {
                title: "Packaging materials",
                text: "Recovered polymer may be used in suitable packaging applications."
            }
        ],

        disposalTitle:
            "Recycling Stream",

        disposalText:
            "Empty the container and follow your local recycling collection rules. Keep different components separated when required.",

        safety:
            "Do not burn plastic waste. Recycling and proper segregation help keep usable material in the recovery stream."

    },


    paper: {

        name: "Paper / Cardboard",

        description:
            "A fibre-based waste item commonly found in household and commercial waste.",

        confidence: "91%",

        category:
            "Paper / Fibre",

        material:
            "Cellulose",

        materialFull:
            "Plant-based cellulose fibres",

        materialsDescription:
            "Paper products are primarily made from cellulose fibres. Coatings, inks, adhesives or mixed materials may also be present depending on the item.",

        materials: [
            {
                name: "Cellulose fibre",
                detail: "Primary paper fibre",
                type: "Fibre"
            },
            {
                name: "Ink / coating",
                detail: "May be present",
                type: "Component"
            }
        ],

        recovery: [
            {
                name: "Paper fibre",
                detail: "Can enter paper recovery streams"
            },
            {
                name: "Cardboard fibre",
                detail: "Can be processed into recycled fibre"
            }
        ],

        uses: [
            {
                title: "Recycled paper",
                text: "Recovered fibres can be used to manufacture new paper products."
            },
            {
                title: "Cardboard",
                text: "Recovered fibre can become feedstock for cardboard and packaging."
            },
            {
                title: "Paper products",
                text: "Recycled fibre can support production of various paper-based goods."
            }
        ],

        disposalTitle:
            "Paper Recycling",

        disposalText:
            "Keep paper dry and place it in the appropriate paper recycling stream where available. Heavily contaminated paper may require different handling.",

        safety:
            "Avoid mixing recyclable paper with wet or heavily contaminated waste."

    },


    glass: {

        name: "Glass Container",

        description:
            "A glass-based container that may be suitable for material recovery.",

        confidence: "89%",

        category:
            "Glass / Container",

        material:
            "Glass",

        materialFull:
            "Silicate-based glass",

        materialsDescription:
            "Glass containers are generally made from a glass composition based on silica and other mineral components. Exact composition varies by product.",

        materials: [
            {
                name: "Glass",
                detail: "Primary material",
                type: "Mineral material"
            },
            {
                name: "Metal / polymer parts",
                detail: "May occur in caps or closures",
                type: "Component"
            }
        ],

        recovery: [
            {
                name: "Glass cullet",
                detail: "Recovered crushed glass"
            },
            {
                name: "Glass container material",
                detail: "Can re-enter glass manufacturing"
            }
        ],

        uses: [
            {
                title: "New glass containers",
                text: "Recovered glass can be processed as feedstock for new glass products."
            },
            {
                title: "Glass products",
                text: "Processed recovered glass can support manufacturing of suitable glass items."
            },
            {
                title: "Construction applications",
                text: "Some processed glass materials can have secondary applications."
            }
        ],

        disposalTitle:
            "Glass Recycling",

        disposalText:
            "Place glass in the appropriate collection stream where glass recycling is available. Handle broken glass carefully.",

        safety:
            "Broken glass can cause injury. Do not place sharp fragments loosely where they could injure collection workers."

    },


    metal: {

        name: "Metal Can",

        description:
            "A metal packaging item that may contain recoverable metal.",

        confidence: "90%",

        category:
            "Metal / Packaging",

        material:
            "Metal",

        materialFull:
            "Metal alloy",

        materialsDescription:
            "Metal packaging may contain materials such as aluminium or steel depending on the product. Exact identification may require additional analysis.",

        materials: [
            {
                name: "Metal",
                detail: "Primary structural material",
                type: "Metal"
            },
            {
                name: "Coating",
                detail: "May be present",
                type: "Surface component"
            }
        ],

        recovery: [
            {
                name: "Metal",
                detail: "Can be recovered through metal recycling"
            },
            {
                name: "Aluminium / steel",
                detail: "Depends on item composition"
            }
        ],

        uses: [
            {
                title: "New metal products",
                text: "Recovered metals can become feedstock for new manufactured products."
            },
            {
                title: "Packaging",
                text: "Recovered metal can potentially re-enter packaging manufacturing."
            },
            {
                title: "Industrial products",
                text: "Recycled metal can support many industrial applications."
            }
        ],

        disposalTitle:
            "Metal Recycling",

        disposalText:
            "Empty the container and place it in the appropriate metal recycling stream where available.",

        safety:
            "Sharp metal edges can cause cuts. Handle damaged containers carefully."
    },


    electronic: {

        name: "Electronic Device",

        description:
            "Electronic waste that may contain several recoverable materials.",

        confidence: "87%",

        category:
            "Electronic Waste",

        material:
            "Mixed Materials",

        materialFull:
            "Metals, polymers, glass and electronic components",

        materialsDescription:
            "Electronic devices can contain a complex mixture of metals, polymers, glass, circuit-board materials and battery components. Exact composition varies significantly between devices.",

        materials: [
            {
                name: "Copper",
                detail: "May occur in wiring and electronics",
                type: "Metal"
            },
            {
                name: "Aluminium",
                detail: "May occur in structural components",
                type: "Metal"
            },
            {
                name: "Battery materials",
                detail: "Depends on battery chemistry",
                type: "Special handling"
            }
        ],

        recovery: [
            {
                name: "Copper",
                detail: "Potentially recoverable by specialized recyclers"
            },
            {
                name: "Aluminium",
                detail: "Potentially recoverable metal"
            },
            {
                name: "Other metals",
                detail: "Recovery depends on device and process"
            },
            {
                name: "Battery materials",
                detail: "Requires specialized handling"
            }
        ],

        uses: [
            {
                title: "Recovered metals",
                text: "Recovered metals can re-enter industrial manufacturing processes."
            },
            {
                title: "Electronic manufacturing",
                text: "Recovered materials can become feedstock for suitable industrial applications."
            },
            {
                title: "Material recovery",
                text: "Specialized recycling can separate useful materials from electronic waste."
            }
        ],

        disposalTitle:
            "Authorized E-Waste Collection",

        disposalText:
            "Do not place electronic devices or batteries into ordinary household waste. Use an appropriate e-waste collection or authorized recycling channel.",

        safety:
            "Do not dismantle batteries or electronic components yourself. Damaged batteries may present fire or chemical hazards."
    }

};


// ================= FILE UPLOAD =================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    if (!file.type.startsWith("image/")) {

        alert("Please choose an image file.");

        return;
    }

    const imageURL =
        URL.createObjectURL(file);

    previewImage.src = imageURL;

    uploadBox.style.display = "none";

    previewContainer.style.display = "block";

    resultsContainer.style.display = "none";

    startScanning(file);

});


// ================= DRAG AND DROP =================

uploadBox.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadBox.classList.add("dragging");

});


uploadBox.addEventListener("dragleave", function () {

    uploadBox.classList.remove("dragging");

});


uploadBox.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadBox.classList.remove("dragging");

    const file = event.dataTransfer.files[0];

    if (!file || !file.type.startsWith("image/")) {

        alert("Please drop an image file.");

        return;
    }

    const imageURL =
        URL.createObjectURL(file);

    previewImage.src = imageURL;

    uploadBox.style.display = "none";

    previewContainer.style.display = "block";

    resultsContainer.style.display = "none";

    startScanning(file);

});


// ================= SCANNING =================

function startScanning(file) {

    const imageWrapper =
        document.querySelector(".image-wrapper");

    imageWrapper.classList.add("scanning");

    progressBar.style.width = "0%";

    progressText.textContent = "0%";

    scanMessage.textContent =
        "Reading image...";

    scanSubMessage.textContent =
        "Preparing visual analysis";

    resetSteps();

    // Start the real AI call immediately in the background
    const aiPromise = analyzeFile(file);

    let progress = 0;

    // Phase 1: animate to 88% while AI is working
    const scanner = setInterval(function () {

        // slow down as we approach 88 so we don't hit the cap too fast
        const increment = progress < 70
            ? Math.floor(Math.random() * 8) + 4
            : Math.floor(Math.random() * 2) + 1;

        progress += increment;

        if (progress > 88) {
            progress = 88;
        }

        progressBar.style.width =
            progress + "%";

        progressText.textContent =
            progress + "%";


        // STEP 1

        if (progress >= 15) {

            completeStep("step1");

            scanMessage.textContent =
                "Image received";

            scanSubMessage.textContent =
                "Visual data loaded successfully";
        }


        // STEP 2

        if (progress >= 40) {

            completeStep("step2");

            scanMessage.textContent =
                "Identifying waste...";

            scanSubMessage.textContent =
                "Analyzing shape and visual characteristics";
        }


        // STEP 3

        if (progress >= 65) {

            completeStep("step3");

            scanMessage.textContent =
                "Analyzing materials...";

            scanSubMessage.textContent =
                "Mapping possible material composition";
        }


        // STEP 4 — stays here, pulsing, until AI responds

        if (progress >= 85) {

            completeStep("step4");

            scanMessage.textContent =
                "Generating guidance...";

            scanSubMessage.textContent =
                "Preparing recovery and disposal information";
        }

    }, 250);

    // Phase 2: when AI responds, stop animation and show result
    aiPromise.then(function (data) {

        clearInterval(scanner);

        progressBar.style.width = "100%";
        progressText.textContent = "100%";

        setTimeout(function () {

            imageWrapper.classList.remove("scanning");

            renderAnalysisResult(data);

        }, 500);

    }).catch(function (error) {

        clearInterval(scanner);

        imageWrapper.classList.remove("scanning");

        showWasteWiseError(error.message);

    });

}


// ================= AI ANALYSIS =================

async function analyzeFile(file) {

    const formData = new FormData();

    formData.append("image", file);

    console.log("WasteWise: sending image to Flask...");

    let response;

    try {

        response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

    } catch (networkError) {

        console.error("WasteWise: network error", networkError);
        throw new Error("Could not reach the WasteWise server. Is Flask running?");

    }

    console.log("WasteWise: Flask responded with status", response.status);

    let data;

    try {

        data = await response.json();

    } catch (parseError) {

        console.error("WasteWise: could not parse response as JSON", parseError);
        throw new Error("The server returned an unreadable response. Please try again.");

    }

    console.log("WasteWise: response data", data);

    if (!response.ok || data.error) {
        throw new Error(data.error || "Analysis failed. Please try again.");
    }

    return data;

}


// ================= SHOW RESULT =================

function showWasteWiseError(message) {

    const imageWrapper =
        document.querySelector(".image-wrapper");

    if (imageWrapper) {
        imageWrapper.classList.remove("scanning");
    }

    scanMessage.textContent = "Analysis Unavailable";

    scanSubMessage.textContent = message;

    document.getElementById("progressBar").style.width = "100%";
    document.getElementById("progressText").textContent = "—";

}


function renderAnalysisResult(data) {

    // BASIC INFORMATION

    document.getElementById("resultName")
        .textContent = data.name;

    document.getElementById("resultDescription")
        .textContent = data.description;

    document.getElementById("confidenceValue")
        .textContent = data.confidence;


    // OVERVIEW

    document.getElementById("overviewName")
        .textContent = data.name;

    document.getElementById("overviewCategory")
        .textContent = data.category;

    document.getElementById("overviewMaterial")
        .textContent = data.material;

    document.getElementById("overviewRecovery")
        .textContent =
        (Array.isArray(data.recovery) && data.recovery.length > 0)
            ? "Recoverable"
            : "Check locally";

    document.getElementById("overviewDisposal")
        .textContent = data.disposalTitle;


    // MATERIALS

    document.getElementById("materialsDescription")
        .textContent = data.materialsDescription;

    const materialList =
        document.getElementById("materialList");

    materialList.innerHTML = "";

    (data.materials || []).forEach(function (item) {

        materialList.innerHTML += `

            <div class="material-item">

                <div>
                    <strong>${item.name}</strong>
                    <small>${item.detail}</small>
                </div>

                <span>${item.type}</span>

            </div>

        `;

    });


    // RECOVERY

    const recoveryGrid =
        document.getElementById("recoveryGrid");

    recoveryGrid.innerHTML = "";

    (data.recovery || []).forEach(function (item) {

        recoveryGrid.innerHTML += `

            <div class="recovery-item">

                <strong>${item.name}</strong>

                <span>
                    ${item.detail}
                </span>

            </div>

        `;

    });


    // POSSIBLE USES

    const usesList =
        document.getElementById("usesList");

    usesList.innerHTML = "";

    (data.uses || []).forEach(function (item, index) {

        const number =
            String(index + 1).padStart(2, "0");

        usesList.innerHTML += `

            <div class="use-item">

                <span>${number}</span>

                <div>

                    <strong>
                        ${item.title}
                    </strong>

                    <p>
                        ${item.text}
                    </p>

                </div>

            </div>

        `;

    });


    // DISPOSAL

    document.getElementById("disposalTitle")
        .textContent = data.disposalTitle;

    document.getElementById("disposalText")
        .textContent = data.disposalText;

    document.getElementById("safetyText")
        .textContent = data.safety;


    // SHOW RESULTS

    resultsContainer.style.display = "block";

    resultsContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// ================= TABS =================

function openTab(tabName, button) {

    const tabs =
        document.querySelectorAll(".tab");

    const contents =
        document.querySelectorAll(".tab-content");


    tabs.forEach(function (tab) {

        tab.classList.remove("active");

    });


    contents.forEach(function (content) {

        content.classList.remove("active");

    });


    button.classList.add("active");

    document.getElementById(tabName)
        .classList.add("active");

}


// ================= RESET =================

function resetScanner() {

    imageInput.value = "";

    uploadBox.style.display = "block";

    previewContainer.style.display = "none";

    resultsContainer.style.display = "none";

    progressBar.style.width = "0%";

    progressText.textContent = "0%";

    resetSteps();

    window.scrollTo({
        top: document.getElementById("scanner").offsetTop - 80,
        behavior: "smooth"
    });

}


// ================= HELPERS =================

function completeStep(id) {

    const element =
        document.getElementById(id);

    element.classList.add("done");

    element.querySelector("span")
        .textContent = "✓";

}


function resetSteps() {

    const steps =
        document.querySelectorAll(".analysis-steps div");

    steps.forEach(function (step) {

        step.classList.remove("done");

        step.querySelector("span")
            .textContent = "○";

    });

}


// ================= NAVIGATION =================

function scrollToScanner() {

    document.getElementById("scanner")
        .scrollIntoView({
            behavior: "smooth"
        });

}


// ================= HOW IT WORKS =================

function showHowItWorks() {

    document.getElementById("how")
        .scrollIntoView({
            behavior: "smooth"
        });

}