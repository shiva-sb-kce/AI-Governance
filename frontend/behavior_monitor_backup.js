(function () {

    "use strict";

    let behaviorView = null;
    let behaviorPoller = null;


    // =========================================================
    // CREATE SIDEBAR NAVIGATION
    // =========================================================

    function createBehaviorNavigation() {

        const sidebarNav = document.querySelector(".sidebar-nav");

        if (!sidebarNav) {
            console.error("Sidebar navigation not found.");
            return;
        }

        // Prevent duplicate creation
        if (document.getElementById("navBehavior")) {
            return;
        }

        const navItem = document.createElement("a");

        navItem.id = "navBehavior";
        navItem.className = "nav-item";
        navItem.href = "#";

        navItem.innerHTML = `
            <span class="nav-icon">🧠</span>
            <span>AI Behavior Monitor</span>
        `;

        // Add AFTER Audit Logs
        const auditNav = document.getElementById("navAudit");

        if (auditNav) {
            auditNav.insertAdjacentElement("afterend", navItem);
        } else {
            sidebarNav.appendChild(navItem);
        }

        navItem.addEventListener("click", function (event) {

            event.preventDefault();

            showBehaviorView();

        });

    }


    // =========================================================
    // CREATE BEHAVIOR VIEW
    // =========================================================

    function createBehaviorView() {

        if (document.getElementById("behaviorView")) {
            behaviorView = document.getElementById("behaviorView");
            return behaviorView;
        }

        const main = document.querySelector(".main");

        if (!main) {
            console.error("Main container not found.");
            return null;
        }

        behaviorView = document.createElement("section");

        behaviorView.id = "behaviorView";
        behaviorView.className = "page-section";

        behaviorView.style.display = "none";

        behaviorView.innerHTML = `

            <header class="topbar">

                <div class="topbar-left">

                    <h1>
                        AI Behavior Monitor
                    </h1>

                    <p>
                        Observe AI actions before execution
                    </p>

                </div>

                <div class="topbar-right">

                    <span
                        id="behaviorLastUpdated"
                        class="last-updated"
                    >
                        Loading...
                    </span>
                    <span
                        id="behaviorGatewayStatus"
                        style="
                            display:flex;
                            align-items:center;
                            gap:7px;
                            font-size:13px;
                            font-weight:700;
                            margin-right:15px;
                        "
                    >
                        <span
                            style="
                                width:8px;
                                height:8px;
                                border-radius:50%;
                                background:#22c55e;
                                display:inline-block;
                            "
                        ></span>

                        Gateway Online
                    </span>

                    <button
                        id="behaviorRefreshBtn"
                        class="refresh-btn"
                        type="button"
                    >
                        ↻ Refresh
                    </button>

                </div>

            </header>


            <!-- =================================================
                 LIVE BEHAVIOR STATUS
                 ================================================= -->

            <section class="stats-grid">

                <div class="stat-card">

                    <div class="stat-card-header">

                        <span>
                            OBSERVED ACTIONS
                        </span>

                        <span class="stat-icon">
                            ◈
                        </span>

                    </div>

                    <div
                        id="behaviorTotal"
                        class="stat-value"
                    >
                        0
                    </div>

                    <div class="stat-label">
                        AI actions received
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-card-header">

                        <span>
                            ALLOWED
                        </span>

                        <span class="stat-icon">
                            ✓
                        </span>

                    </div>

                    <div
                        id="behaviorAllowed"
                        class="stat-value"
                    >
                        0
                    </div>

                    <div class="stat-label">
                        Actions permitted
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-card-header">

                        <span>
                            BLOCKED
                        </span>

                        <span class="stat-icon">
                            ⛔
                        </span>

                    </div>

                    <div
                        id="behaviorBlocked"
                        class="stat-value"
                    >
                        0
                    </div>

                    <div class="stat-label">
                        Actions prevented
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-card-header">

                        <span>
                            APPROVAL
                        </span>

                        <span class="stat-icon">
                            !
                        </span>

                    </div>

                    <div
                        id="behaviorApproval"
                        class="stat-value"
                    >
                        0
                    </div>

                    <div class="stat-label">
                        Awaiting human approval
                    </div>

                </div>

            </section>


            <!-- =================================================
                 BEHAVIOR SCENARIOS
                 ================================================= -->

            <section class="panel">

                <div class="panel-header">

                    <div>

                        <h2>
                            Connected AI Sources
                        </h2>

                        <span>
                            AI actions observed by the governance gateway
                        </span>

                    </div>

                </div>

                <div
                    id="behaviorScenarioList"
                    class="list-container"
                >

                    <div class="list-row">
                        Loading behavior sources...
                    </div>

                </div>

            </section>


            <!-- =================================================
                 RECENT AI BEHAVIOR
                 ================================================= -->

            <section class="panel">

                <div class="panel-header">

                    <div>

                        <h2>
                            Recent AI Behavior
                        </h2>

                        <span>
                            Latest actions intercepted by the governance gateway
                        </span>

                    </div>

                </div>


                <div class="table-container">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Time
                                </th>

                                <th>
                                    Agent
                                </th>

                                <th>
                                    Action
                                </th>

                                <th>
                                    Resource
                                </th>

                                <th>
                                    Decision
                                </th>

                                <th>
                                    Risk
                                </th>

                                <th>
                                    Execution
                                </th>

                            </tr>

                        </thead>

                        <tbody
                            id="behaviorTable"
                        >

                            <tr>

                                <td colspan="7">
                                    Loading behavior...
                                </td>

                            </tr>

                        </tbody>

                    </table>

                </div>

            </section>


            <!-- =================================================
                 GOVERNANCE FLOW
                 ================================================= -->

            <section class="panel">

                <div class="panel-header">

                    <div>

                        <h2>
                            Behavior → Governance Flow
                        </h2>

                        <span>
                            Every observable AI action passes through the security layer
                        </span>

                    </div>

                </div>


                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    gap:18px;
                    flex-wrap:wrap;
                    padding:30px;
                    font-weight:600;
                ">

                    <div class="stat-card">
                        🧠 AI Agent
                    </div>

                    <span>→</span>

                    <div class="stat-card">
                        👁 Behavior Gateway
                    </div>

                    <span>→</span>

                    <div class="stat-card">
                        🛡 Governance Engine
                    </div>

                    <span>→</span>

                    <div class="stat-card">
                        ⚖ Decision
                    </div>

                    <span>→</span>

                    <div class="stat-card">
                        ▶ Execution
                    </div>

                </div>

            </section>


            <footer>

                <span>
                    Unified AI Governance &
                    Security Platform
                </span>

                <span>
                    Behavior Monitoring • Risk • Governance
                </span>

            </footer>

        `;

        main.appendChild(behaviorView);

        return behaviorView;

    }


    // =========================================================
    // SHOW BEHAVIOR VIEW
    // =========================================================

    function showBehaviorView() {

        createBehaviorView();

        const dashboardView =
            document.getElementById("dashboardView");

        const securityView =
            document.getElementById("securityEvaluationView");

        const approvalSection =
            document.getElementById("approvalSection");

        const navItems =
            document.querySelectorAll(".nav-item");


        // Hide complete dashboard
        if (dashboardView) {
            dashboardView.style.display = "none";
        }

        // Hide behavior initially before showing
        if (behaviorView) {
            behaviorView.style.display = "block";
        }


        // Hide other independent sections
        if (securityView) {
            securityView.style.display = "none";
        }

        if (approvalSection) {
            approvalSection.style.display = "none";
        }


        // Update active navigation
        navItems.forEach(function (item) {
            item.classList.remove("active");
        });

        const behaviorNav =
            document.getElementById("navBehavior");

        if (behaviorNav) {
            behaviorNav.classList.add("active");
        }


        loadBehaviorData();

        startBehaviorPolling();

    }


    // =========================================================
    // LOAD BEHAVIOR DATA
    // =========================================================

    async function loadBehaviorData() {

        try {

            const response = await fetch(
                "/behavior/recent?limit=20"
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to load behavior data"
                );
            }

            const data =
                await response.json();

            renderBehaviorEvents(
                data.events || []
            );

            updateBehaviorStats(
                data.events || []
            );

            const lastUpdated =
                document.getElementById(
                    "behaviorLastUpdated"
                );

            if (lastUpdated) {

                lastUpdated.textContent =
                    "Updated " +
                    new Date().toLocaleTimeString();

            }

        } catch (error) {

            console.error(
                "Behavior monitor error:",
                error
            );

        }

    }


    // =========================================================
    // LOAD SCENARIOS
    // =========================================================

    async function loadBehaviorScenarios() {

        const container =
            document.getElementById(
                "behaviorScenarioList"
            );

        if (!container) {
            return;
        }

        try {

            const response = await fetch(
                "/behavior/scenarios"
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to load scenarios"
                );
            }

            const data =
                await response.json();

            const scenarios =
                data.scenarios || [];


            if (!scenarios.length) {

                container.innerHTML = `
                    <div class="list-row">
                        No behavior scenarios available.
                    </div>
                `;

                return;

            }


            container.innerHTML =
                scenarios.map(function (scenario) {

                    return `

                        <div
                            class="list-row"
                            style="
                                display:flex;
                                align-items:center;
                                justify-content:space-between;
                                gap:15px;
                                flex-wrap:wrap;
                            "
                        >

                            <div>

                                <strong>
                                    ${escapeHtml(
                                        scenario.name
                                    )}
                                </strong>

                                <div
                                    style="
                                        font-size:13px;
                                        opacity:.7;
                                        margin-top:4px;
                                    "
                                >
                                    ${escapeHtml(
                                        scenario.description
                                    )}
                                </div>

                            </div>


                            <div
                                style="
                                    display:flex;
                                    align-items:center;
                                    gap:8px;
                                    font-size:12px;
                                    font-weight:700;
                                "
                            >

                                <span
                                    style="
                                        width:8px;
                                        height:8px;
                                        border-radius:50%;
                                        background:#22c55e;
                                        display:inline-block;
                                    "
                                ></span>

                                OBSERVED BY GATEWAY

                            </div>

                        </div>

                    `;

                }).join("");


        } catch (error) {

            console.error(
                "Scenario loading error:",
                error
            );

            container.innerHTML = `
                <div class="list-row">
                    Unable to load behavior scenarios.
                </div>
            `;

        }

    }


    // =========================================================
    // SEND BEHAVIOR
    // =========================================================

    async function sendBehavior(scenario) {

        try {

            const response = await fetch(
                "/behavior/demo/" +
                encodeURIComponent(scenario),
                {
                    method: "POST"
                }
            );

            const data =
                await response.json();

            console.log(
                "Behavior governance result:",
                data
            );

            await loadBehaviorData();

            showGovernanceResult(data);

        } catch (error) {

            console.error(
                "Behavior submission failed:",
                error
            );

        }

    }


    // =========================================================
    // GOVERNANCE RESULT
    // =========================================================

    function showGovernanceResult(data) {

        const governance =
            data.governance || {};

        const decision =
            governance.decision ||
            "UNKNOWN";

        const approvalId =
            governance.approval_id ||
            "-";

        const reasons =
            governance.reasons || [];


        alert(
            "AI Behavior Governance Result\n\n" +

            "Agent: " +
            (
                data.scenario?.agent_id ||
                "-"
            ) +

            "\nAction: " +
            (
                data.scenario?.tool ||
                "-"
            ) +

            "\nDecision: " +
            decision +

            "\nApproval ID: " +
            approvalId +

            "\n\n" +

            (
                reasons.length
                    ? reasons.join("\n")
                    : "No additional reasons."
            )
        );

    }


    // =========================================================
    // RENDER EVENTS
    // =========================================================

    function renderBehaviorEvents(events) {

        const table =
            document.getElementById(
                "behaviorTable"
            );

        if (!table) {
            return;
        }


        if (!events.length) {

            table.innerHTML = `
                <tr>
                    <td colspan="7">
                        No AI behavior detected yet.
                    </td>
                </tr>
            `;

            return;

        }


        table.innerHTML =
            events.map(function (event) {
                const decision =
                    typeof event.decision === "object"
                        ? (
                            event.decision?.value ||
                            event.decision?.name ||
                            "-"
                        )
                        : (
                            event.decision ||
                            event.governance_decision ||
                            "-"
                        );


                const risk =
                    typeof event.risk === "object"
                        ? (
                            event.risk?.score ??
                            event.risk?.risk_score ??
                            event.risk?.value ??
                            "-"
                        )
                        : (
                            event.risk_score ??
                            event.risk ??
                            "-"
                        );


                let execution =
                    event.execution_status || "";

                execution = String(
                    execution
                ).toUpperCase();

                if (execution === "EXECUTED") {

                    execution = "EXECUTED";

                }
                else if (execution === "PENDING_APPROVAL") {

                    execution = "PENDING APPROVAL";

                }
                else if (execution === "BLOCKED") {

                    execution = "BLOCKED";

                }
                else if (
                    execution === "EXECUTION_NOT_RECORDED"
                ) {

                    execution = "NOT RECORDED";

                }
                else if (!execution) {

                    execution = "NOT RECORDED";

                }

                const time =
                    event.timestamp
                        ? new Date(
                            event.timestamp
                        ).toLocaleTimeString()
                        : "-";


                return `

                    <tr>

                        <td>
                            ${escapeHtml(time)}
                        </td>

                        <td>
                            ${escapeHtml(
                                typeof event.agent_id === "object"
                                    ? (
                                        event.agent_id?.id ||
                                        event.agent_id?.name ||
                                        event.agent_id?.value ||
                                        "-"
                                    )
                                    : (
                                        event.agent_id ||
                                        event.entity ||
                                        "-"
                                    )
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                event.action ||
                                "-"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                event.resource ||
                                "-"
                            )}
                        </td>

                        <td>
                            <strong>
                                ${escapeHtml(
                                    decision
                                )}
                            </strong>
                        </td>

                        <td>
                            ${escapeHtml(
                                String(risk)
                            )}
                        </td>

                        <td>

                            <strong
                                style="
                                    font-size:12px;
                                    font-weight:700;
                                "
                            >
                                ${escapeHtml(execution)}
                            </strong>

                        </td>

                    </tr>

                `;

            }).join("");

    }


    // =========================================================
    // UPDATE STATS
    // =========================================================

    function updateBehaviorStats(events) {

        let allowed = 0;
        let blocked = 0;
        let approval = 0;


        events.forEach(function (event) {

            let decision = event.decision;

            if (typeof decision === "object") {

                decision =
                    decision?.value ||
                    decision?.name ||
                    "";

            }

            decision = String(
                decision
            ).toUpperCase();


            if (decision === "ALLOW") {
                allowed++;
            }

            else if (decision === "BLOCK") {
                blocked++;
            }

            else if (decision === "APPROVAL") {
                approval++;
            }

        });


        const total =
            events.length;


        const totalElement =
            document.getElementById(
                "behaviorTotal"
            );

        const allowedElement =
            document.getElementById(
                "behaviorAllowed"
            );

        const blockedElement =
            document.getElementById(
                "behaviorBlocked"
            );

        const approvalElement =
            document.getElementById(
                "behaviorApproval"
            );


        if (totalElement) {
            totalElement.textContent = total;
        }

        if (allowedElement) {
            allowedElement.textContent =
                allowed;
        }

        if (blockedElement) {
            blockedElement.textContent =
                blocked;
        }

        if (approvalElement) {
            approvalElement.textContent =
                approval;
        }

    }


    // =========================================================
    // POLLING
    // =========================================================

    function startBehaviorPolling() {

        stopBehaviorPolling();

        behaviorPoller =
            setInterval(
                function () {

                    if (
                        behaviorView &&
                        behaviorView.style.display !==
                        "none"
                    ) {

                        loadBehaviorData();

                    }

                },
                5000
            );

    }


    function stopBehaviorPolling() {

        if (behaviorPoller) {

            clearInterval(
                behaviorPoller
            );

            behaviorPoller = null;

        }

    }


    // =========================================================
    // ESCAPE HTML
    // =========================================================

    function escapeHtml(value) {

        return String(value ?? "")
            .replace(
                /&/g,
                "&amp;"
            )
            .replace(
                /</g,
                "&lt;"
            )
            .replace(
                />/g,
                "&gt;"
            )
            .replace(
                /"/g,
                "&quot;"
            )
            .replace(
                /'/g,
                "&#039;"
            );

    }


    // =========================================================
    // INITIALIZE
    // =========================================================

    function initializeBehaviorMonitor() {

        createBehaviorNavigation();

        createBehaviorView();

        loadBehaviorScenarios();


        // Refresh button
        document.addEventListener(
            "click",
            function (event) {

                if (
                    event.target &&
                    event.target.id ===
                    "behaviorRefreshBtn"
                ) {

                    loadBehaviorData();

                }

            }
        );


        // Dashboard navigation
        const dashboardNav =
            document.getElementById(
                "navDashboard"
            );

        if (dashboardNav) {

            dashboardNav.addEventListener(
                "click",
                function () {

                    stopBehaviorPolling();

                    if (behaviorView) {
                        behaviorView.style.display =
                            "none";
                    }

                }
            );

        }

    }


    // =========================================================
    // START
    // =========================================================

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeBehaviorMonitor
        );

    } else {

        initializeBehaviorMonitor();

    }

})();

async function checkBehaviorGateway() {

    const status =
        document.getElementById(
            "behaviorGatewayStatus"
        );

    if (!status) {
        return;
    }

    try {

        const response = await fetch(
            "/behavior/scenarios",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                "Gateway unavailable"
            );
        }

        status.innerHTML = `
            <span
                style="
                    width:8px;
                    height:8px;
                    border-radius:50%;
                    background:#22c55e;
                    display:inline-block;
                "
            ></span>

            Gateway Online
        `;

    } catch (error) {

        status.innerHTML = `
            <span
                style="
                    width:8px;
                    height:8px;
                    border-radius:50%;
                    background:#ef4444;
                    display:inline-block;
                "
            ></span>

            Gateway Offline
        `;

    }

}