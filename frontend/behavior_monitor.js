(function () {
    "use strict";

    let behaviorView = null;
    let behaviorPoller = null;
    let initialized = false;

    const $ = (id) => document.getElementById(id);

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function getDecision(event) {
        const value = event?.decision;

        if (value && typeof value === "object") {
            return String(
                value.value ||
                value.name ||
                "-"
            ).toUpperCase();
        }

        return String(
            value ||
            event?.governance_decision ||
            "-"
        ).toUpperCase();
    }

    function getRisk(event) {
        if (
            event?.risk &&
            typeof event.risk === "object"
        ) {
            return (
                event.risk.score ??
                event.risk.risk_score ??
                event.risk.value ??
                "-"
            );
        }

        return (
            event?.risk_score ??
            event?.risk ??
            "-"
        );
    }

    function getAgent(event) {

        if (
            event?.agent_id &&
            typeof event.agent_id !== "object"
        ) {
            return String(event.agent_id);
        }

        if (
            event?.agent_id &&
            typeof event.agent_id === "object"
        ) {
            return String(
                event.agent_id.id ||
                event.agent_id.name ||
                event.agent_id.value ||
                "-"
            );
        }

        if (
            event?.entity &&
            typeof event.entity === "object"
        ) {
            return String(
                event.entity.id ||
                event.entity.name ||
                event.entity.value ||
                "-"
            );
        }

        if (
            typeof event?.entity === "string"
        ) {
            return event.entity;
        }

        return "-";
    }

    function getExecution(event, decision) {

        let status =
            event?.execution_status;

        if (
            status &&
            typeof status === "object"
        ) {
            status =
                status.status ||
                status.value ||
                "";
        }

        status = String(
            status || ""
        ).toUpperCase();

        if (
            [
                "SUCCESS",
                "EXECUTED",
                "COMPLETED"
            ].includes(status)
        ) {
            return "EXECUTED";
        }

        if (
            status === "PENDING_APPROVAL"
        ) {
            return "PENDING APPROVAL";
        }

        if (
            status === "BLOCKED"
        ) {
            return "BLOCKED";
        }

        if (
            !status &&
            decision === "APPROVAL"
        ) {
            return "PENDING APPROVAL";
        }

        if (
            !status &&
            decision === "BLOCK"
        ) {
            return "BLOCKED";
        }

        if (
            !status &&
            decision === "ALLOW"
        ) {
            return "NOT RECORDED";
        }

        return status || "NOT RECORDED";
    }

    // ========================================================
    // SIDEBAR
    // ========================================================

    function createNavigation() {

        const sidebar =
            document.querySelector(
                ".sidebar-nav"
            );

        if (
            !sidebar ||
            $("navBehavior")
        ) {
            return;
        }

        const item =
            document.createElement("a");

        item.id = "navBehavior";

        item.className = "nav-item";

        item.href = "#";

        item.innerHTML = `
            <span class="nav-icon">🧠</span>
            <span>AI Behavior Monitor</span>
        `;

        const audit =
            $("navAudit");

        if (audit) {

            audit.insertAdjacentElement(
                "afterend",
                item
            );

        } else {

            sidebar.appendChild(item);

        }

        item.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showView();

            }
        );
    }

    // ========================================================
    // CREATE VIEW
    // ========================================================

    function createView() {

        if ($("behaviorView")) {

            behaviorView =
                $("behaviorView");

            return;
        }

        const main =
            document.querySelector(".main");

        if (!main) {
            return;
        }

        behaviorView =
            document.createElement("section");

        behaviorView.id =
            "behaviorView";

        behaviorView.className =
            "page-section";

        behaviorView.style.display =
            "none";

        behaviorView.innerHTML = `

<header class="topbar">

    <div class="topbar-left">

        <h1>
            AI Behavior Monitor
        </h1>

        <p>
            Observe local AI actions before execution
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
            "
        >
            Checking...
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


<!-- =====================================================
     QWEN PANEL
===================================================== -->

<section class="panel">

    <div class="panel-header">

        <div>

            <h2>
                Local Qwen3:8B Agent
            </h2>

            <span>
                Qwen proposes the action;
                Governance decides whether it may execute.
            </span>

        </div>


        <span
            id="qwenStatus"
            class="evaluation-status"
        >
            CHECKING
        </span>

    </div>


    <div style="padding:20px 22px;">

        <label
            for="qwenInstruction"
            style="
                display:block;
                font-size:12px;
                font-weight:800;
                margin-bottom:8px;
            "
        >
            Natural-language instruction
        </label>


        <textarea
            id="qwenInstruction"
            rows="3"
            style="
                width:100%;
                resize:vertical;
                border:1px solid #e5e7eb;
                border-radius:9px;
                padding:12px;
            "
        >Read the file demo.txt</textarea>


        <div
            style="
                display:flex;
                align-items:center;
                gap:10px;
                flex-wrap:wrap;
                margin-top:12px;
            "
        >

            <button
                id="qwenRunBtn"
                class="refresh-btn"
                type="button"
            >
                ▶ Run Qwen Agent
            </button>


            <span
                id="qwenResultText"
                style="
                    font-size:12px;
                    color:#6b7280;
                "
            >
                Qwen will decide which tool action to request.
            </span>

        </div>


        <pre
            id="qwenResult"
            style="
                display:none;
                margin-top:16px;
                padding:14px;
                background:#f8fafc;
                border:1px solid #e5e7eb;
                border-radius:9px;
                white-space:pre-wrap;
                word-break:break-word;
                font-size:12px;
            "
        ></pre>

    </div>

</section>


<!-- =====================================================
     AI ACTION SIMULATOR
===================================================== -->

<section class="panel">

    <div class="panel-header">

        <div>

            <h2>
                AI Action Simulator
            </h2>

            <span>
                Simulate an AI-generated action that requires human approval
            </span>

        </div>

        <span
            style="
                font-size:12px;
                font-weight:800;
                padding:6px 10px;
                border-radius:999px;
                background:#fff7ed;
                color:#c2410c;
            "
        >
            HUMAN-IN-THE-LOOP
        </span>

    </div>


    <div
        style="
            padding:20px 22px;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:20px;
            flex-wrap:wrap;
        "
    >

        <div
            style="
                flex:1;
                min-width:260px;
            "
        >

            <div
                style="
                    font-size:13px;
                    font-weight:800;
                    margin-bottom:8px;
                "
            >
                Report Agent
            </div>

            <div
                style="
                    font-size:13px;
                    color:#6b7280;
                    line-height:1.6;
                "
            >
                AI proposes
                <strong>write_file</strong>
                on
                <strong>behavior_report.txt</strong>.
                The action must pass Action Governance before execution.
            </div>

        </div>


        <button
            id="requestActionApprovalBtn"
            class="refresh-btn"
            type="button"
        >
            🛡 Request Human Approval
        </button>

    </div>


    <div
        id="actionSimulatorStatus"
        style="
            display:none;
            margin:0 22px 20px;
            padding:12px 14px;
            border-radius:9px;
            background:#f8fafc;
            border:1px solid #e5e7eb;
            font-size:12px;
            line-height:1.5;
        "
    ></div>

</section>


<!-- =====================================================
     STATISTICS
===================================================== -->

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


<!-- =====================================================
     CONNECTED AI SOURCES
===================================================== -->

<section class="panel">

    <div class="panel-header">

        <div>

            <h2>
                Connected AI Sources
            </h2>

            <span>
                AI sources routed through the governance gateway
            </span>

        </div>

    </div>


    <div
        id="behaviorScenarioList"
        class="list-container"
    >

        <div class="list-row">
            Loading...
        </div>

    </div>

</section>


<!-- =====================================================
     RECENT AI BEHAVIOR
===================================================== -->

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


            <tbody id="behaviorTable">

                <tr>

                    <td colspan="7">
                        Loading behavior...
                    </td>

                </tr>

            </tbody>

        </table>

    </div>

</section>


<!-- =====================================================
     FLOW
===================================================== -->

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


    <div
        style="
            display:flex;
            align-items:center;
            justify-content:center;
            gap:18px;
            flex-wrap:wrap;
            padding:30px;
            font-weight:600;
        "
    >

        <div class="stat-card">
            🧠 Qwen3:8B
        </div>

        <span>
            →
        </span>

        <div class="stat-card">
            👁 Behavior Gateway
        </div>

        <span>
            →
        </span>

        <div class="stat-card">
            🛡 Governance Engine
        </div>

        <span>
            →
        </span>

        <div class="stat-card">
            ⚖ ALLOW / APPROVAL / BLOCK
        </div>

        <span>
            →
        </span>

        <div class="stat-card">
            ▶ Secure Executor
        </div>

    </div>

</section>


<footer>

    <span>
        Unified AI Governance & Security Platform
    </span>

    <span>
        Local AI • Behavior • Risk • Governance
    </span>

</footer>

`;

        main.appendChild(
            behaviorView
        );
    }

    // ========================================================
    // SHOW VIEW
    // ========================================================

    function showView() {

        createView();

        const dashboard =
            $("dashboardView");

        const security =
            $("securityEvaluationView");

        const approval =
            $("approvalSection");


        if (dashboard) {
            dashboard.style.display =
                "none";
        }

        if (security) {
            security.style.display =
                "none";
        }

        if (approval) {
            approval.style.display =
                "none";
        }


        if (behaviorView) {
            behaviorView.style.display =
                "block";
        }


        document
            .querySelectorAll(".nav-item")
            .forEach(
                item =>
                    item.classList.remove(
                        "active"
                    )
            );


        const nav =
            $("navBehavior");

        if (nav) {
            nav.classList.add("active");
        }


        loadBehavior();

        loadSources();

        checkStatus();

        startPolling();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }

    // ========================================================
    // LOAD BEHAVIOR
    // ========================================================

    async function loadBehavior() {

        try {

            const response =
                await fetch(
                    "/behavior/recent?limit=20",
                    {
                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Behavior API failed: ${response.status}`
                );

            }


            const data =
                await response.json();


            const events =
                Array.isArray(data.events)
                    ? data.events
                    : [];


            renderEvents(events);

            updateStats(events);


            const updated =
                $("behaviorLastUpdated");


            if (updated) {

                updated.textContent =
                    "Updated " +
                    new Date()
                        .toLocaleTimeString();

            }

        } catch (error) {

            console.error(
                "[Behavior Monitor]",
                error
            );

        }
    }

    // ========================================================
    // LOAD SOURCES
    // ========================================================

    async function loadSources() {

        const box =
            $("behaviorScenarioList");

        if (!box) {
            return;
        }


        try {

            const response =
                await fetch(
                    "/behavior/scenarios",
                    {
                        cache: "no-store"
                    }
                );


            const data =
                await response.json();


            const scenarios =
                Array.isArray(
                    data.scenarios
                )
                    ? data.scenarios
                    : [];


            if (!scenarios.length) {

                box.innerHTML = `
                    <div class="list-row">
                        No behavior sources available.
                    </div>
                `;

                return;
            }


            box.innerHTML =
                scenarios
                    .map(
                        scenario => `
<div class="list-row">

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
                margin-right:6px;
            "
        ></span>

        GATEWAY CONNECTED

    </div>

</div>
`
                    )
                    .join("");

        } catch (error) {

            console.error(
                "[Behavior Sources]",
                error
            );


            box.innerHTML = `
                <div class="list-row">
                    Unable to load behavior sources.
                </div>
            `;
        }
    }

    // ========================================================
    // STATUS
    // ========================================================

    async function checkStatus() {

        const gateway =
            $("behaviorGatewayStatus");

        const qwen =
            $("qwenStatus");


        try {

            const response =
                await fetch(
                    "/behavior/scenarios",
                    {
                        cache: "no-store"
                    }
                );


            if (!response.ok) {
                throw new Error();
            }


            if (gateway) {

                gateway.innerHTML = `
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
            }

        } catch (_) {

            if (gateway) {

                gateway.innerHTML = `
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


        try {

            const response =
                await fetch(
                    "/ai/qwen/health",
                    {
                        cache: "no-store"
                    }
                );


            const data =
                await response.json();


            if (qwen) {

                qwen.textContent =
                    data.status === "online"
                        ? "ONLINE"
                        : "OFFLINE";


                qwen.className =
                    "evaluation-status " +
                    (
                        data.status === "online"
                            ? "pass"
                            : "review"
                    );
            }

        } catch (_) {

            if (qwen) {

                qwen.textContent =
                    "OFFLINE";

                qwen.className =
                    "evaluation-status review";
            }
        }
    }

    // ========================================================
    // RUN QWEN
    // ========================================================

    async function runQwen() {

        const instructionElement =
            $("qwenInstruction");

        const button =
            $("qwenRunBtn");

        const text =
            $("qwenResultText");

        const result =
            $("qwenResult");


        const instruction =
            instructionElement
                ?.value
                .trim();


        if (!instruction) {

            alert(
                "Enter a natural-language instruction for Qwen."
            );

            return;
        }


        if (button) {

            button.disabled =
                true;

            button.textContent =
                "Running Qwen...";

        }


        if (text) {

            text.textContent =
                "Qwen is deciding the action and sending it to governance...";

        }


        try {

            const response =
                await fetch(
                    "/ai/qwen",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                instruction:
                                    instruction,

                                request_id:
                                    "QWEN-" +
                                    Date.now(),

                                agent_id:
                                    "qwen-agent"

                            })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data?.detail ||
                    `Qwen request failed: ${response.status}`
                );
            }


            if (result) {

                result.style.display =
                    "block";

                result.textContent =
                    JSON.stringify(
                        data,
                        null,
                        2
                    );

            }


            const governance =
                data?.governance ||
                {};


            let decision =
                governance.decision;


            if (
                decision &&
                typeof decision === "object"
            ) {

                decision =
                    decision.value ||
                    decision.name;

            }


            if (text) {

                text.textContent =
                    "Governance result: " +
                    String(
                        decision ||
                        data?.status ||
                        "UNKNOWN"
                    ).toUpperCase();

            }


            await loadBehavior();

            await checkStatus();


        } catch (error) {

            console.error(
                "[Qwen Agent]",
                error
            );


            if (text) {

                text.textContent =
                    "Qwen request failed: " +
                    error.message;

            }


            if (result) {

                result.style.display =
                    "block";

                result.textContent =
                    error.message;

            }

        } finally {

            if (button) {

                button.disabled =
                    false;

                button.textContent =
                    "▶ Run Qwen Agent";

            }
        }
    }

    // ========================================================
    // REQUEST AI ACTION APPROVAL
    // ========================================================

    async function requestActionApproval() {

        const button =
            $("requestActionApprovalBtn");

        const status =
            $("actionSimulatorStatus");


        if (button) {

            button.disabled =
                true;

            button.textContent =
                "Requesting Approval...";

        }


        if (status) {

            status.style.display =
                "block";

            status.textContent =
                "Sending Report Agent action through Action Governance...";

        }


        try {

            const response =
                await fetch(
                    "/behavior/demo/file_write",
                    {
                        method: "POST",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        cache: "no-store"
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data?.detail ||
                    `Action request failed: ${response.status}`
                );
            }


            const governance =
                data?.governance ||
                {};


            let decision =
                governance.decision ||
                data?.decision ||
                data?.status ||
                "UNKNOWN";


            if (
                decision &&
                typeof decision === "object"
            ) {

                decision =
                    decision.value ||
                    decision.name ||
                    "UNKNOWN";

            }


            decision =
                String(
                    decision
                ).toUpperCase();


            if (status) {

                if (
                    decision ===
                    "APPROVAL"
                ) {

                    status.innerHTML = `
                        <strong>
                            ⏳ Human approval required.
                        </strong>
                        The action has been stopped before execution.
                        Open <strong>Approvals</strong> to review and approve it.
                    `;

                } else if (
                    decision ===
                    "BLOCK"
                ) {

                    status.innerHTML = `
                        <strong>
                            🛡 Action blocked.
                        </strong>
                        Governance prevented execution.
                    `;

                } else {

                    status.innerHTML = `
                        <strong>
                            Governance result: ${escapeHtml(decision)}
                        </strong>
                    `;
                }

            }


            await loadBehavior();

            await checkStatus();


            /*
             * Give the user a clear visual indication
             * that the request was successfully created.
             */
            if (
                decision ===
                "APPROVAL"
            ) {

                setTimeout(
                    function () {

                        if (status) {

                            status.innerHTML += `
                                <br>
                                <span
                                    style="
                                        display:inline-block;
                                        margin-top:6px;
                                        font-weight:700;
                                    "
                                >
                                    → Go to Approvals and click
                                    <strong>Approve & Execute</strong>.
                                </span>
                            `;

                        }

                    },
                    300
                );
            }


        } catch (error) {

            console.error(
                "[AI Action Simulator]",
                error
            );


            if (status) {

                status.style.display =
                    "block";

                status.innerHTML = `
                    <strong>
                        Action request failed.
                    </strong>
                    ${escapeHtml(
                        error.message
                    )}
                `;
            }

        } finally {

            if (button) {

                button.disabled =
                    false;

                button.textContent =
                    "🛡 Request Human Approval";

            }
        }
    }

    // ========================================================
    // RENDER EVENTS
    // ========================================================

    function renderEvents(events) {

        const table =
            $("behaviorTable");


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
            events
                .map(
                    event => {

                        const decision =
                            getDecision(
                                event
                            );


                        const risk =
                            getRisk(
                                event
                            );


                        const execution =
                            getExecution(
                                event,
                                decision
                            );


                        const agent =
                            getAgent(
                                event
                            );


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
        ${escapeHtml(agent)}
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

        <span
            class="
                decision-badge
                badge-${escapeHtml(
                    decision.toLowerCase()
                )}
            "
        >
            ${escapeHtml(
                decision
            )}
        </span>

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
            "
        >
            ${escapeHtml(
                execution
            )}
        </strong>

    </td>

</tr>
`;
                    }
                )
                .join("");
    }

    // ========================================================
    // STATISTICS
    // ========================================================

    function updateStats(events) {

        let allowed =
            0;

        let blocked =
            0;

        let approval =
            0;


        events.forEach(
            event => {

                const decision =
                    getDecision(
                        event
                    );


                if (
                    decision === "ALLOW"
                ) {

                    allowed++;

                } else if (
                    decision === "BLOCK"
                ) {

                    blocked++;

                } else if (
                    decision === "APPROVAL"
                ) {

                    approval++;

                }

            }
        );


        if ($("behaviorTotal")) {

            $("behaviorTotal")
                .textContent =
                events.length;

        }


        if ($("behaviorAllowed")) {

            $("behaviorAllowed")
                .textContent =
                allowed;

        }


        if ($("behaviorBlocked")) {

            $("behaviorBlocked")
                .textContent =
                blocked;

        }


        if ($("behaviorApproval")) {

            $("behaviorApproval")
                .textContent =
                approval;

        }
    }

    // ========================================================
    // POLLING
    // ========================================================

    function startPolling() {

        stopPolling();


        behaviorPoller =
            setInterval(
                function () {

                    if (
                        behaviorView &&
                        behaviorView.style.display !==
                            "none"
                    ) {

                        loadBehavior();

                        checkStatus();

                    }

                },
                5000
            );
    }


    function stopPolling() {

        if (behaviorPoller) {

            clearInterval(
                behaviorPoller
            );

            behaviorPoller =
                null;
        }
    }

    // ========================================================
    // INITIALIZE
    // ========================================================

    function initialize() {

        if (initialized) {
            return;
        }


        initialized =
            true;


        createNavigation();

        createView();


        document.addEventListener(
            "click",
            function (event) {

                if (
                    event.target?.id ===
                    "behaviorRefreshBtn"
                ) {

                    loadBehavior();

                    loadSources();

                    checkStatus();

                }


                if (
                    event.target?.id ===
                    "qwenRunBtn"
                ) {

                    runQwen();

                }


                if (
                    event.target?.id ===
                    "requestActionApprovalBtn"
                ) {

                    requestActionApproval();

                }

            }
        );


        const dashboard =
            $("navDashboard");


        if (dashboard) {

            dashboard.addEventListener(
                "click",
                function () {

                    stopPolling();

                    if (behaviorView) {

                        behaviorView.style.display =
                            "none";

                    }

                }
            );

        }
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            {
                once: true
            }
        );

    } else {

        initialize();

    }

})();