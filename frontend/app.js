// ============================================================
// UNIFIED AI GOVERNANCE & SECURITY PLATFORM
// FRONTEND CONTROLLER
// ============================================================

"use strict";


// ============================================================
// CONFIGURATION
// ============================================================

const API = "";

const REFRESH_INTERVAL = 5000;


// ============================================================
// GLOBAL STATE
// ============================================================

let currentView = "dashboard";

let refreshTimer = null;

let appInitialized = false;

let dashboardLoading = false;
let securityLoading = false;
let approvalsLoading = false;
let auditLoading = false;


// ============================================================
// GENERIC API HELPER
// ============================================================

async function fetchJSON(url, options = {}) {

    const response = await fetch(
        url,
        {
            cache: "no-store",

            ...options,

            headers: {
                "Accept": "application/json",
                ...(options.headers || {})
            }
        }
    );


    let data = null;

    try {

        data = await response.json();

    } catch (_) {

        data = null;
    }


    if (!response.ok) {

        const message =
            data?.detail ||
            data?.message ||
            `Request failed: ${response.status}`;

        throw new Error(message);
    }


    return data;
}


// ============================================================
// DASHBOARD
// ============================================================

async function loadDashboard() {

    if (dashboardLoading) {
        return;
    }


    dashboardLoading = true;


    const lastUpdated =
        document.getElementById(
            "lastUpdated"
        );


    try {

        console.log(
            "[Dashboard] Loading..."
        );


        const data =
            await fetchJSON(
                `${API}/dashboard`
            );


        console.log(
            "[Dashboard] Response:",
            data
        );


        updateSummary(data);

        updateDecisions(
            data.decisions || {}
        );

        updateThreats(
            data.threats || {}
        );

        updateEntities(
            data.entities || {}
        );

        updateActions(
            data.actions || {}
        );


        await loadRecentActivity();


        if (lastUpdated) {

            lastUpdated.textContent =
                `Updated ${new Date().toLocaleTimeString()}`;
        }

    } catch (error) {

        console.error(
            "[Dashboard] Error:",
            error
        );


        if (lastUpdated) {

            lastUpdated.textContent =
                `Connection error: ${error.message}`;
        }

    } finally {

        dashboardLoading = false;
    }
}


// ============================================================
// DASHBOARD SUMMARY
// ============================================================

function updateSummary(data) {

    const totalEvents =
        document.getElementById(
            "totalEvents"
        );


    const blocked =
        document.getElementById(
            "blocked"
        );


    const approvals =
        document.getElementById(
            "approvals"
        );


    const averageRisk =
        document.getElementById(
            "averageRisk"
        );


    const decisions =
        data.decisions || {};


    if (totalEvents) {

        totalEvents.textContent =
            formatNumber(
                data.total_events ?? 0
            );
    }


    if (blocked) {

        blocked.textContent =
            formatNumber(
                decisions.BLOCK ?? 0
            );
    }


    if (approvals) {

        approvals.textContent =
            formatNumber(
                decisions.APPROVAL ?? 0
            );
    }


    if (averageRisk) {

        averageRisk.textContent =
            formatRisk(
                data.average_risk
            );
    }
}


// ============================================================
// DECISION DISTRIBUTION
// ============================================================

function updateDecisions(decisions) {

    const allow =
        Number(
            decisions.ALLOW ?? 0
        );


    const block =
        Number(
            decisions.BLOCK ?? 0
        );


    const approval =
        Number(
            decisions.APPROVAL ?? 0
        );


    const monitor =
        Number(
            decisions.MONITOR ?? 0
        );


    const max =
        Math.max(
            allow,
            block,
            approval,
            monitor,
            1
        );


    setDecision(
        "allow",
        allow,
        max
    );


    setDecision(
        "block",
        block,
        max
    );


    setDecision(
        "approval",
        approval,
        max
    );


    setDecision(
        "monitor",
        monitor,
        max
    );
}


function setDecision(
    name,
    value,
    max
) {

    const count =
        document.getElementById(
            `${name}Count`
        );


    const bar =
        document.getElementById(
            `${name}Bar`
        );


    if (count) {

        count.textContent =
            formatNumber(value);
    }


    if (bar) {

        const percentage =
            Math.max(
                0,
                Math.min(
                    100,
                    (value / max) * 100
                )
            );


        bar.style.width =
            `${percentage}%`;
    }
}


// ============================================================
// THREATS
// ============================================================

function updateThreats(threats) {

    const container =
        document.getElementById(
            "threatList"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const entries =
        Object.entries(
            threats || {}
        );


    if (entries.length === 0) {

        container.innerHTML = `
            <div class="list-row">

                <span class="list-name">
                    No threats detected
                </span>

                <span class="list-value">
                    0
                </span>

            </div>
        `;

        return;
    }


    entries
        .sort(
            (a, b) =>
                Number(b[1]) -
                Number(a[1])
        )
        .forEach(
            ([name, value]) => {

                const row =
                    document.createElement(
                        "div"
                    );


                row.className =
                    "list-row";


                row.innerHTML = `
                    <span class="list-name">
                        ${escapeHtml(
                            formatName(name)
                        )}
                    </span>

                    <span class="list-value">
                        ${formatNumber(value)}
                    </span>
                `;


                container.appendChild(
                    row
                );
            }
        );
}


// ============================================================
// ENTITIES
// ============================================================

function updateEntities(entities) {

    const container =
        document.getElementById(
            "entityList"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const entries =
        Object.entries(
            entities || {}
        );


    if (entries.length === 0) {

        container.innerHTML = `
            <div class="list-row">

                <span class="list-name">
                    No entity activity
                </span>

                <span class="list-value">
                    0
                </span>

            </div>
        `;

        return;
    }


    entries
        .sort(
            (a, b) =>
                Number(b[1]) -
                Number(a[1])
        )
        .forEach(
            ([name, value]) => {

                const row =
                    document.createElement(
                        "div"
                    );


                row.className =
                    "list-row";


                row.innerHTML = `
                    <span class="list-name">
                        ${escapeHtml(
                            formatName(name)
                        )}
                    </span>

                    <span class="list-value">
                        ${formatNumber(value)}
                    </span>
                `;


                container.appendChild(
                    row
                );
            }
        );
}


// ============================================================
// ACTIONS
// ============================================================

function updateActions(actions) {

    const container =
        document.getElementById(
            "actionList"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const entries =
        Object.entries(
            actions || {}
        );


    if (entries.length === 0) {

        container.innerHTML = `
            <div class="list-row">

                <span class="list-name">
                    No action activity
                </span>

                <span class="list-value">
                    0
                </span>

            </div>
        `;

        return;
    }


    entries
        .sort(
            (a, b) =>
                Number(b[1]) -
                Number(a[1])
        )
        .forEach(
            ([name, value]) => {

                const row =
                    document.createElement(
                        "div"
                    );


                row.className =
                    "list-row";


                row.innerHTML = `
                    <span class="list-name">
                        ${escapeHtml(
                            formatName(name)
                        )}
                    </span>

                    <span class="list-value">
                        ${formatNumber(value)}
                    </span>
                `;


                container.appendChild(
                    row
                );
            }
        );
}


// ============================================================
// RECENT ACTIVITY
// ============================================================

async function loadRecentActivity() {

    const table =
        document.getElementById(
            "activityTable"
        );


    if (!table) {
        return;
    }


    try {

        const data =
            await fetchJSON(
                `${API}/dashboard/recent?limit=15`
            );


        renderActivity(
            data.events || []
        );

    } catch (error) {

        console.error(
            "[Activity] Error:",
            error
        );


        table.innerHTML = `
            <tr>

                <td colspan="6">

                    Unable to load activity.

                    <br>

                    <small>
                        ${escapeHtml(
                            error.message
                        )}
                    </small>

                </td>

            </tr>
        `;
    }
}


function renderActivity(events) {

    const table =
        document.getElementById(
            "activityTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    if (
        !Array.isArray(events) ||
        events.length === 0
    ) {

        table.innerHTML = `
            <tr>

                <td colspan="6">
                    No activity recorded
                </td>

            </tr>
        `;

        return;
    }


    events.forEach(
        event => {

            const entity =
                event.entity || {};


            const risk =
                event.risk || {};


            const entityType =
                entity.type ||
                event.entity_type ||
                "-";


            const action =
                event.action ||
                "-";


            const decision =
                event.decision ||
                "-";


            const riskScore =
                risk.score ??
                event.risk_score ??
                "-";


            const eventType =
                event.event_type ||
                "-";


            const timestamp =
                formatAuditTimestamp(
                    event.timestamp
                );


            const badge =
                String(
                    decision
                )
                    .toLowerCase();


            const riskClass =
                getRiskClass(
                    riskScore
                );


            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `
                <td>
                    ${escapeHtml(
                        timestamp
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        formatName(
                            entityType
                        )
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        formatName(
                            action
                        )
                    )}
                </td>

                <td>
                    <span
                        class="
                            decision-badge
                            badge-${escapeHtml(
                                badge
                            )}
                        "
                    >
                        ${escapeHtml(
                            decision
                        )}
                    </span>
                </td>

                <td>
                    <span
                        class="${escapeHtml(
                            riskClass
                        )}"
                    >
                        ${escapeHtml(
                            riskScore
                        )}
                    </span>
                </td>

                <td>
                    ${escapeHtml(
                        formatName(
                            eventType
                        )
                    )}
                </td>
            `;


            table.appendChild(
                row
            );
        }
    );
}


// ============================================================
// SECURITY EVALUATION
// ============================================================

async function loadSecurityEvaluation() {

    if (securityLoading) {
        return;
    }


    securityLoading = true;


    const status =
        document.getElementById(
            "evaluationStatus"
        );


    const table =
        document.getElementById(
            "evaluationTable"
        );


    const scenarioCount =
        document.getElementById(
            "evaluationScenarioCount"
        );


    if (status) {

        status.textContent =
            "LOADING";

        status.className =
            "evaluation-status";
    }


    try {

        console.log(
            "[Security] Loading evaluation..."
        );


        const data =
            await fetchJSON(
                `${API}/evaluation/security`
            );


        console.log(
            "[Security] Response:",
            data
        );


        updateEvaluation(
            data
        );


    } catch (error) {

        console.error(
            "[Security] Error:",
            error
        );


        if (status) {

            status.textContent =
                "ERROR";

            status.className =
                "evaluation-status review";
        }


        if (scenarioCount) {

            scenarioCount.textContent =
                "Evaluation unavailable";
        }


        if (table) {

            table.innerHTML = `
                <tr>

                    <td colspan="7">

                        Unable to load evaluation.

                        <br><br>

                        <small>
                            ${escapeHtml(
                                error.message
                            )}
                        </small>

                    </td>

                </tr>
            `;
        }

    } finally {

        securityLoading = false;
    }
}


// ============================================================
// UPDATE SECURITY EVALUATION
// ============================================================

function updateEvaluation(data) {

    if (
        !data ||
        typeof data !== "object"
    ) {

        throw new Error(
            "Invalid evaluation response."
        );
    }


    const metrics =
        data.metrics || {};


    setSecurityMetric(
        "evalAccuracy",
        metrics.accuracy
    );


    setSecurityMetric(
        "evalPrecision",
        metrics.precision
    );


    setSecurityMetric(
        "evalRecall",
        metrics.recall
    );


    setSecurityMetric(
        "evalF1",
        metrics.f1 ??
        metrics.f1_score
    );


    setSecurityMetric(
        "evalDetection",
        metrics.attack_detection_rate
    );


    setSecurityMetric(
        "evalFPR",
        metrics.false_positive_rate
    );


    setSecurityText(
        "evalTP",
        metrics.true_positive
    );


    setSecurityText(
        "evalTN",
        metrics.true_negative
    );


    setSecurityText(
        "evalFP",
        metrics.false_positive
    );


    setSecurityText(
        "evalFN",
        metrics.false_negative
    );


    const scenarios =
        Array.isArray(
            data.scenarios
        )
            ? data.scenarios
            : [];


    setSecurityText(
        "evaluationScenarioCount",
        `${scenarios.length} scenarios`
    );


    renderEvaluationScenarios(
        scenarios
    );


    const allCorrect =
        scenarios.length > 0 &&
        scenarios.every(
            scenario =>
                scenario.correct === true
        );


    const status =
        document.getElementById(
            "evaluationStatus"
        );


    if (status) {

        status.textContent =
            allCorrect
                ? "STRONG"
                : "REVIEW";


        status.className =
            allCorrect
                ? "evaluation-status pass"
                : "evaluation-status review";
    }
}


// ============================================================
// SECURITY METRIC
// ============================================================

function setSecurityMetric(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {
        return;
    }


    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        element.textContent =
            "-";

        return;
    }


    const number =
        Number(value);


    if (!Number.isFinite(number)) {

        element.textContent =
            "-";

        return;
    }


    const percentage =
        Math.abs(number) <= 1
            ? number * 100
            : number;


    element.textContent =
        `${percentage.toFixed(2)}%`;
}


// ============================================================
// SECURITY TEXT
// ============================================================

function setSecurityText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {
        return;
    }


    element.textContent =
        value === null ||
        value === undefined
            ? "-"
            : String(value);
}


// ============================================================
// SECURITY SCENARIO TABLE
// ============================================================

function renderEvaluationScenarios(
    scenarios
) {

    const table =
        document.getElementById(
            "evaluationTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    if (
        !Array.isArray(
            scenarios
        ) ||
        scenarios.length === 0
    ) {

        table.innerHTML = `
            <tr>

                <td colspan="7">
                    No evaluation results
                </td>

            </tr>
        `;

        return;
    }


    scenarios.forEach(
        scenario => {

            const correct =
                scenario.correct === true;


            const status =
                correct
                    ? "PASS"
                    : "FAIL";


            const statusClass =
                correct
                    ? "eval-pass"
                    : "eval-fail";


            const expected =
                scenario.expected_malicious === true
                    ? "MALICIOUS"
                    : "BENIGN";


            const predicted =
                scenario.predicted_malicious === true
                    ? "MALICIOUS"
                    : "BENIGN";


            const decision =
                scenario.decision ||
                "-";


            const riskScore =
                scenario.risk_score ??
                "-";


            const badge =
                String(
                    decision
                )
                    .toLowerCase();


            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `
                <td>
                    ${escapeHtml(
                        scenario.scenario_id ??
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        scenario.name ??
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        expected
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        predicted
                    )}
                </td>

                <td>
                    <span
                        class="
                            decision-badge
                            badge-${escapeHtml(
                                badge
                            )}
                        "
                    >
                        ${escapeHtml(
                            decision
                        )}
                    </span>
                </td>

                <td>
                    <span
                        class="${escapeHtml(
                            getRiskClass(
                                riskScore
                            )
                        )}"
                    >
                        ${escapeHtml(
                            riskScore
                        )}
                    </span>
                </td>

                <td>
                    <span
                        class="${statusClass}"
                    >
                        ${status}
                    </span>
                </td>
            `;


            table.appendChild(
                row
            );
        }
    );
}


// ============================================================
// APPROVAL CENTER
// ============================================================

async function loadApprovals() {

    if (approvalsLoading) {
        return;
    }


    approvalsLoading = true;


    const container =
        document.getElementById(
            "pendingApprovalList"
        );


    if (!container) {

        approvalsLoading = false;

        return;
    }


    container.innerHTML = `
        <div class="approval-empty">
            Loading approvals...
        </div>
    `;


    try {

        console.log(
            "[Approvals] Loading..."
        );


        const data =
            await fetchJSON(
                `${API}/approval/pending`
            );


        const approvals =
            Array.isArray(
                data?.approvals
            )
                ? data.approvals
                : [];


        updatePendingApprovalCount(
            approvals.length
        );


        renderApprovals(
            approvals
        );


        const updated =
            document.getElementById(
                "approvalLastUpdated"
            );


        if (updated) {

            updated.textContent =
                `Updated ${new Date().toLocaleTimeString()}`;
        }


    } catch (error) {

        console.error(
            "[Approvals] Error:",
            error
        );


        updatePendingApprovalCount(
            0
        );


        container.innerHTML = `
            <div class="approval-error">

                Unable to load pending approvals.

                <br><br>

                <small>
                    ${escapeHtml(
                        error.message
                    )}
                </small>

            </div>
        `;

    } finally {

        approvalsLoading = false;
    }
}


// ============================================================
// PENDING APPROVAL COUNT
// ============================================================

function updatePendingApprovalCount(
    count
) {

    const element =
        document.getElementById(
            "pendingApprovalCount"
        );


    if (element) {

        element.textContent =
            formatNumber(
                count
            );
    }
}


// ============================================================
// RENDER APPROVALS
// ============================================================

function renderApprovals(
    approvals
) {

    const container =
        document.getElementById(
            "pendingApprovalList"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !Array.isArray(
            approvals
        ) ||
        approvals.length === 0
    ) {

        container.innerHTML = `
            <div class="approval-empty">

                <div class="empty-icon">
                    ✓
                </div>

                <h3>
                    No Pending Approvals
                </h3>

                <p>
                    All governance actions
                    have been reviewed.
                </p>

            </div>
        `;

        return;
    }


    approvals.forEach(
        approval => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "approval-card";


            const approvalId =
                approval.approval_id ||
                approval.id ||
                "-";


            const action =
                approval.action ||
                approval.tool ||
                "-";


            const agent =
                approval.agent_id ||
                approval.entity?.id ||
                "-";


            const resource =
                approval.resource ||
                approval.parameters?.path ||
                "-";


            const risk =
                approval.risk_score ??
                approval.risk?.score ??
                "-";


            const status =
                approval.status ||
                "PENDING";


            const parameters =
                approval.parameters || {};


            card.innerHTML = `
                <div class="approval-header">

                    <div>

                        <h3>
                            ${escapeHtml(
                                formatName(action)
                            )}
                        </h3>

                        <span class="approval-status">
                            ${escapeHtml(
                                formatName(status)
                            )}
                        </span>

                    </div>

                    <span
                        class="${escapeHtml(
                            getRiskClass(risk)
                        )}"
                    >
                        Risk ${escapeHtml(risk)}
                    </span>

                </div>


                <div class="approval-details">

                    <div>
                        <strong>
                            Approval ID
                        </strong>

                        <span>
                            ${escapeHtml(
                                approvalId
                            )}
                        </span>
                    </div>


                    <div>
                        <strong>
                            Agent
                        </strong>

                        <span>
                            ${escapeHtml(
                                agent
                            )}
                        </span>
                    </div>


                    <div>
                        <strong>
                            Resource
                        </strong>

                        <span>
                            ${escapeHtml(
                                resource
                            )}
                        </span>
                    </div>


                    <div>
                        <strong>
                            Parameters
                        </strong>

                        <span>
                            ${escapeHtml(
                                formatParameterValue(
                                    parameters
                                )
                            )}
                        </span>
                    </div>

                </div>


                <div class="approval-actions">

                    <button
                        type="button"
                        class="approval-btn approve-btn"
                        data-action="approve"
                        data-approval-id="${escapeHtml(
                            approvalId
                        )}"
                    >
                        ✓ Approve & Execute
                    </button>


                    <button
                        type="button"
                        class="approval-btn deny-btn"
                        data-action="deny"
                        data-approval-id="${escapeHtml(
                            approvalId
                        )}"
                    >
                        ✕ Deny
                    </button>

                </div>
            `;


            container.appendChild(
                card
            );
        }
    );


    setupApprovalButtons();
}


// ============================================================
// APPROVAL BUTTON HANDLERS
// ============================================================

function setupApprovalButtons() {

    const buttons =
        document.querySelectorAll(
            "#pendingApprovalList [data-action][data-approval-id]"
        );


    buttons.forEach(
        button => {

            button.onclick =
                async () => {

                    const approvalId =
                        button.dataset.approvalId;


                    const action =
                        button.dataset.action;


                    if (!approvalId) {
                        return;
                    }


                    if (
                        action ===
                        "approve"
                    ) {

                        await approveApproval(
                            approvalId,
                            button
                        );

                    } else if (
                        action ===
                        "deny"
                    ) {

                        await denyApproval(
                            approvalId,
                            button
                        );
                    }
                };
        }
    );
}


// ============================================================
// APPROVE ACTION
// ============================================================

async function approveApproval(
    approvalId,
    button
) {

    const approverId =
        window.prompt(
            "Enter approver ID:"
        );


    if (!approverId) {
        return;
    }


    const confirmed =
        window.confirm(
            "Approve this action?\n\n" +
            "The approved action will be executed."
        );


    if (!confirmed) {
        return;
    }


    const originalText =
        button
            ? button.textContent
            : "";


    if (button) {

        button.disabled =
            true;

        button.textContent =
            "Approving...";
    }


    try {

        const data =
            await fetchJSON(
                `${API}/approval/${encodeURIComponent(
                    approvalId
                )}/approve`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        approver_id:
                            approverId
                    })
                }
            );


        if (
            data?.executed === true
        ) {

            window.alert(
                "✓ Approval successful.\n\n" +
                "The action was executed."
            );

        } else {

            window.alert(
                "⚠ Approval processed,\n" +
                "but the action was not executed."
            );
        }


        await loadApprovals();


        await loadDashboard();


        if (
            currentView ===
            "audit"
        ) {

            await loadAuditLogs();
        }

    } catch (error) {

        console.error(
            "[Approvals] Approval error:",
            error
        );


        window.alert(
            `Approval failed:\n${error.message}`
        );

    } finally {

        if (button) {

            button.disabled =
                false;

            button.textContent =
                originalText;
        }
    }
}


// ============================================================
// DENY ACTION
// ============================================================

async function denyApproval(
    approvalId,
    button
) {

    const approverId =
        window.prompt(
            "Enter approver ID:"
        );


    if (!approverId) {
        return;
    }


    const confirmed =
        window.confirm(
            "Deny this action?\n\n" +
            "The action will NOT be executed."
        );


    if (!confirmed) {
        return;
    }


    const originalText =
        button
            ? button.textContent
            : "";


    if (button) {

        button.disabled =
            true;

        button.textContent =
            "Denying...";
    }


    try {

        await fetchJSON(
            `${API}/approval/${encodeURIComponent(
                approvalId
            )}/deny`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    approver_id:
                        approverId
                })
            }
        );


        window.alert(
            "✓ Action denied.\n\n" +
            "The action was NOT executed."
        );


        await loadApprovals();


        await loadDashboard();


        if (
            currentView ===
            "audit"
        ) {

            await loadAuditLogs();
        }

    } catch (error) {

        console.error(
            "[Approvals] Denial error:",
            error
        );


        window.alert(
            `Denial failed:\n${error.message}`
        );

    } finally {

        if (button) {

            button.disabled =
                false;

            button.textContent =
                originalText;
        }
    }
}


// ============================================================
// AUDIT LOGS
// ============================================================

async function loadAuditLogs() {

    if (auditLoading) {
        return;
    }


    auditLoading = true;


    const table =
        document.getElementById(
            "auditTable"
        );


    if (table) {

        table.innerHTML = `
            <tr>

                <td colspan="9">
                    Loading audit logs...
                </td>

            </tr>
        `;
    }


    try {

        console.log(
            "[Audit] Loading..."
        );


        const data =
            await fetchJSON(
                `${API}/audit/recent?limit=100`
            );


        const events =
            Array.isArray(
                data?.events
            )
                ? data.events
                : [];


        updateAuditSummary(
            events
        );


        renderAuditLogs(
            events
        );


        const updated =
            document.getElementById(
                "auditLastUpdated"
            );


        if (updated) {

            updated.textContent =
                `Updated ${new Date().toLocaleTimeString()}`;
        }

    } catch (error) {

        console.error(
            "[Audit] Error:",
            error
        );


        if (table) {

            table.innerHTML = `
                <tr>

                    <td colspan="9">

                        Unable to load audit logs.

                        <br><br>

                        <small>
                            ${escapeHtml(
                                error.message
                            )}
                        </small>

                    </td>

                </tr>
            `;
        }

    } finally {

        auditLoading = false;
    }
}


// ============================================================
// AUDIT SUMMARY
// ============================================================

function updateAuditSummary(
    events
) {

    let blocked = 0;

    let approvals = 0;

    let allowed = 0;


    events.forEach(
        event => {

            const decision =
                String(
                    event.decision || ""
                ).toUpperCase();


            if (
                decision ===
                "BLOCK"
            ) {

                blocked++;

            } else if (
                decision ===
                "APPROVAL"
            ) {

                approvals++;

            } else if (
                decision ===
                "ALLOW"
            ) {

                allowed++;
            }
        }
    );


    setAuditText(
        "auditTotal",
        events.length
    );


    setAuditText(
        "auditBlocked",
        blocked
    );


    setAuditText(
        "auditApprovals",
        approvals
    );


    setAuditText(
        "auditAllowed",
        allowed
    );
}


// ============================================================
// AUDIT TABLE
// ============================================================

function renderAuditLogs(
    events
) {

    const table =
        document.getElementById(
            "auditTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    if (
        !Array.isArray(events) ||
        events.length === 0
    ) {

        table.innerHTML = `
            <tr>

                <td colspan="9">

                    No audit events recorded.

                </td>

            </tr>
        `;

        return;
    }


    events.forEach(
        event => {

            const entity =
                event.entity || {};


            const risk =
                event.risk || {};


            const approval =
                event.approval_id ||
                "-";


            const decision =
                event.decision ||
                "-";


            const riskScore =
                risk.score ??
                event.risk_score ??
                "-";


            const badge =
                String(
                    decision
                )
                    .toLowerCase();


            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `
                <td>
                    ${escapeHtml(
                        formatAuditTimestamp(
                            event.timestamp
                        )
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        event.audit_id ??
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        event.request_id ??
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        formatName(
                            entity.type ||
                            "-"
                        )
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        formatName(
                            event.action ||
                            "-"
                        )
                    )}
                </td>

                <td>
                    <span
                        class="
                            decision-badge
                            badge-${escapeHtml(
                                badge
                            )}
                        "
                    >
                        ${escapeHtml(
                            decision
                        )}
                    </span>
                </td>

                <td>
                    <span
                        class="${escapeHtml(
                            getRiskClass(
                                riskScore
                            )
                        )}"
                    >
                        ${escapeHtml(
                            riskScore
                        )}
                    </span>
                </td>

                <td>
                    ${escapeHtml(
                        approval
                    )}
                </td>

                <td>
                    <button
                        type="button"
                        class="audit-details-btn"
                        data-audit-details="true"
                        data-audit-id="${escapeHtml(
                            event.audit_id ??
                            ""
                        )}"
                    >
                        View
                    </button>
                </td>
            `;


            table.appendChild(
                row
            );
        }
    );


    setupAuditDetailsButtons(
        events
    );
}


// ============================================================
// AUDIT DETAILS BUTTONS
// ============================================================

function setupAuditDetailsButtons(
    events
) {

    const buttons =
        document.querySelectorAll(
            "#auditTable [data-audit-details='true']"
        );


    buttons.forEach(
        button => {

            button.onclick =
                () => {

                    const auditId =
                        button.dataset.auditId;


                    const event =
                        events.find(
                            item =>
                                String(
                                    item.audit_id
                                ) ===
                                String(
                                    auditId
                                )
                        );


                    if (event) {

                        showAuditDetails(
                            event
                        );
                    }
                };
        }
    );
}


// ============================================================
// AUDIT DETAILS
// ============================================================

function showAuditDetails(
    event
) {

    const panel =
        document.getElementById(
            "auditDetailsPanel"
        );


    const title =
        document.getElementById(
            "auditDetailsTitle"
        );


    const content =
        document.getElementById(
            "auditDetailsContent"
        );


    if (
        !panel ||
        !content
    ) {
        return;
    }


    if (title) {

        title.textContent =
            event.audit_id ||
            "Audit Event";
    }


    content.textContent =
        JSON.stringify(
            event,
            null,
            2
        );


    panel.style.display =
        "block";


    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ============================================================
// AUDIT TEXT
// ============================================================

function setAuditText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {
        return;
    }


    element.textContent =
        value ?? "-";
}


// ============================================================
// NAVIGATION
// ============================================================

function setupNavigation() {

    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );


    navItems.forEach(
        item => {

            item.addEventListener(
                "click",
                event => {

                    event.preventDefault();


                    const id =
                        item.id;


                    switch (id) {

                        case "navDashboard":

                            showDashboardView(
                                navItems
                            );

                            break;


                        case "navSecurity":

                            showSecurityView(
                                navItems
                            );

                            break;


                        case "navApprovals":

                            showApprovalView(
                                navItems
                            );

                            break;


                        case "navAudit":

                            showAuditView(
                                navItems
                            );

                            break;


                        default:

                            console.warn(
                                "Unknown navigation item:",
                                id
                            );
                    }
                }
            );
        }
    );
}


// ============================================================
// HIDE ALL VIEWS
// ============================================================

function hideAllViews() {

    const dashboardView =
        document.getElementById(
            "dashboardView"
        );


    const approvalSection =
        document.getElementById(
            "approvalSection"
        );


    const approvalsView =
        document.getElementById(
            "approvalsView"
        );


    const auditView =
        document.getElementById(
            "auditView"
        );


    const placeholderView =
        document.getElementById(
            "placeholderView"
        );


    if (dashboardView) {

        dashboardView.style.display =
            "none";
    }


    if (approvalSection) {

        approvalSection.style.display =
            "none";
    }


    if (approvalsView) {

        approvalsView.style.display =
            "none";
    }


    if (auditView) {

        auditView.style.display =
            "none";
    }


    if (placeholderView) {

        placeholderView.style.display =
            "none";
    }
}


// ============================================================
// DASHBOARD VIEW
// ============================================================

function showDashboardView(navItems) {

    currentView = "dashboard";

    setActiveNavigation(
        navItems,
        "dashboard"
    );


    const dashboardView =
        document.getElementById(
            "dashboardView"
        );

    if (dashboardView) {

        dashboardView.style.display =
            "block";
    }


    // Show normal dashboard elements
    const dashboardTopbar =
        document.querySelector(
            "#dashboardView > .topbar"
        );

    const statsGrid =
        document.querySelector(
            "#dashboardView > .stats-grid"
        );

    const threeColumnGrid =
        document.querySelector(
            "#dashboardView > .three-column-grid"
        );

    const footer =
        document.querySelector(
            "#dashboardView > footer"
        );


    if (dashboardTopbar) {

        dashboardTopbar.style.display =
            "flex";
    }


    if (statsGrid) {

        statsGrid.style.display =
            "grid";
    }


    if (threeColumnGrid) {

        threeColumnGrid.style.display =
            "grid";
    }


    if (footer) {

        footer.style.display =
            "flex";
    }


    // Hide Approval Center
    const approvalSection =
        document.getElementById(
            "approvalSection"
        );

    if (approvalSection) {

        approvalSection.style.display =
            "none";
    }


    // Show dashboard panels
    const panels =
        document.querySelectorAll(
            "#dashboardView > .panel"
        );


    panels.forEach(
        panel => {

            if (
                panel.id !==
                "approvalSection"
            ) {

                panel.style.display =
                    "block";
            }
        }
    );


    loadDashboard();


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showSecurityView(navItems) {

    currentView = "security";

    setActiveNavigation(
        navItems,
        "security"
    );


    // Dashboard parent must stay visible
    const dashboardView =
        document.getElementById(
            "dashboardView"
        );

    if (dashboardView) {

        dashboardView.style.display =
            "block";
    }


    // Hide dashboard normal content
    const dashboardTopbar =
        document.querySelector(
            "#dashboardView > .topbar"
        );

    const statsGrid =
        document.querySelector(
            "#dashboardView > .stats-grid"
        );

    const threeColumnGrid =
        document.querySelector(
            "#dashboardView > .three-column-grid"
        );

    const footer =
        document.querySelector(
            "#dashboardView > footer"
        );


    if (dashboardTopbar) {

        dashboardTopbar.style.display =
            "none";
    }


    if (statsGrid) {

        statsGrid.style.display =
            "none";
    }


    if (threeColumnGrid) {

        threeColumnGrid.style.display =
            "none";
    }


    if (footer) {

        footer.style.display =
            "none";
    }


    // Hide all panels
    const panels =
        document.querySelectorAll(
            "#dashboardView > .panel"
        );


    panels.forEach(
        panel => {

            panel.style.display =
                "none";
        }
    );


    // Show Security Evaluation
    const securityEvaluation =
        document.getElementById(
            "securityEvaluationView"
        );


    if (securityEvaluation) {

        securityEvaluation.style.display =
            "block";
    }


    // Load backend evaluation
    loadSecurityEvaluation();


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


// ============================================================
// APPROVAL VIEW
// ============================================================

function showApprovalView(navItems) {

    currentView = "approvals";

    // Active sidebar item
    setActiveNavigation(
        navItems,
        "approvals"
    );

    /*
     * IMPORTANT:
     * approvalSection is inside dashboardView.
     *
     * So dashboardView MUST remain visible.
     */
    const dashboardView =
        document.getElementById(
            "dashboardView"
        );

    if (dashboardView) {

        dashboardView.style.display =
            "block";
    }


    // Hide dashboard-only content
    const dashboardTopbar =
        document.querySelector(
            "#dashboardView > .topbar"
        );

    const statsGrid =
        document.querySelector(
            "#dashboardView > .stats-grid"
        );

    const panels =
        document.querySelectorAll(
            "#dashboardView > .panel"
        );

    const threeColumnGrid =
        document.querySelector(
            "#dashboardView > .three-column-grid"
        );

    const footer =
        document.querySelector(
            "#dashboardView > footer"
        );


    if (dashboardTopbar) {

        dashboardTopbar.style.display =
            "none";
    }


    if (statsGrid) {

        statsGrid.style.display =
            "none";
    }


    if (threeColumnGrid) {

        threeColumnGrid.style.display =
            "none";
    }


    if (footer) {

        footer.style.display =
            "none";
    }


    /*
     * Hide all dashboard panels
     * except Approval Center.
     */
    panels.forEach(
        panel => {

            if (
                panel.id !==
                "approvalSection" &&
                !panel.classList.contains(
                    "approval-panel"
                )
            ) {

                panel.style.display =
                    "none";
            }
        }
    );


    // Show Approval Center
    const approvalSection =
        document.getElementById(
            "approvalSection"
        );

    if (approvalSection) {

        approvalSection.style.display =
            "block";
    }


    // Load real backend approvals
    loadApprovals();


    // Go to top
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}
// ============================================================
// AUDIT VIEW
// ============================================================

function showAuditView(
    navItems
) {

    currentView =
        "audit";


    setActiveNavigation(
        navItems,
        "audit"
    );


    hideAllViews();


    let auditView =
        document.getElementById(
            "auditView"
        );


    if (!auditView) {

        auditView =
            document.createElement(
                "section"
            );


        auditView.id =
            "auditView";


        auditView.className =
            "page-section";


        const main =
            document.querySelector(
                ".main"
            );


        if (!main) {

            console.error(
                "[Audit] Main container not found."
            );

            return;
        }


        main.appendChild(
            auditView
        );
    }


    auditView.style.display =
        "block";


    auditView.innerHTML = `

        <div class="topbar">

            <div>

                <h2>
                    Audit Logs
                </h2>

                <p>
                    Governance activity,
                    security decisions and
                    compliance history
                </p>

            </div>


            <div>

                <button
                    id="auditRefreshBtn"
                    class="refresh-btn"
                    type="button"
                >
                    ↻ Refresh
                </button>

            </div>

        </div>


        <section class="approval-summary">

            <div class="approval-summary-card">

                <span>
                    Total Events
                </span>

                <strong id="auditTotal">
                    -
                </strong>

            </div>


            <div class="approval-summary-card">

                <span>
                    Blocked
                </span>

                <strong id="auditBlocked">
                    -
                </strong>

            </div>


            <div class="approval-summary-card">

                <span>
                    Approvals
                </span>

                <strong id="auditApprovals">
                    -
                </strong>

            </div>


            <div class="approval-summary-card">

                <span>
                    Allowed
                </span>

                <strong id="auditAllowed">
                    -
                </strong>

            </div>

        </section>


        <section class="panel">

            <div class="panel-header">

                <div>

                    <h3>
                        Recent Audit Events
                    </h3>

                    <span>
                        Latest governance and
                        security decisions
                    </span>

                </div>


                <span
                    id="auditLastUpdated"
                    class="last-updated"
                >
                    -
                </span>

            </div>


            <div class="table-container">

                <table>

                    <thead>

                        <tr>

                            <th>
                                Time
                            </th>

                            <th>
                                Audit ID
                            </th>

                            <th>
                                Request ID
                            </th>

                            <th>
                                Entity
                            </th>

                            <th>
                                Action
                            </th>

                            <th>
                                Decision
                            </th>

                            <th>
                                Risk
                            </th>

                            <th>
                                Approval
                            </th>

                            <th>
                                Details
                            </th>

                        </tr>

                    </thead>


                    <tbody id="auditTable">

                        <tr>

                            <td colspan="9">
                                Loading audit logs...
                            </td>

                        </tr>

                    </tbody>

                </table>

            </div>

        </section>


        <section
            id="auditDetailsPanel"
            class="panel"
            style="display:none;"
        >

            <div class="panel-header">

                <div>

                    <h3>
                        Audit Event Details
                    </h3>

                    <span
                        id="auditDetailsTitle"
                    >
                        -
                    </span>

                </div>

            </div>


            <pre
                id="auditDetailsContent"
                style="
                    white-space:pre-wrap;
                    word-break:break-word;
                    overflow:auto;
                    padding:20px;
                "
            ></pre>

        </section>


        <footer>

            <span>
                Unified AI Governance &
                Security Platform
            </span>

            <span>
                Audit & Compliance Monitoring
            </span>

        </footer>
    `;


    const refreshButton =
        document.getElementById(
            "auditRefreshBtn"
        );


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadAuditLogs
        );
    }


    loadAuditLogs();


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


// ============================================================
// ACTIVE NAVIGATION
// ============================================================

function setActiveNavigation(
    navItems,
    target
) {

    navItems.forEach(
        nav => {

            nav.classList.remove(
                "active"
            );
        }
    );


    const targetElement =
        document.getElementById(
            `nav${capitalize(target)}`
        );


    if (targetElement) {

        targetElement.classList.add(
            "active"
        );

        return;
    }


    navItems.forEach(
        nav => {

            const text =
                nav.textContent
                    .trim()
                    .toLowerCase();


            if (
                text.includes(
                    target.toLowerCase()
                )
            ) {

                nav.classList.add(
                    "active"
                );
            }
        }
    );
}


// ============================================================
// HELPERS
// ============================================================

function formatNumber(
    value
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(
            number
        )
    ) {

        return "0";
    }


    return number.toLocaleString();
}


function formatRisk(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "--";
    }


    const number =
        Number(value);


    if (
        !Number.isFinite(
            number
        )
    ) {

        return "--";
    }


    return number.toFixed(2);
}


function formatName(
    value
) {

    if (!value) {
        return "-";
    }


    return String(value)
        .replaceAll(
            "_",
            " "
        )
        .replace(
            /\b\w/g,
            char =>
                char.toUpperCase()
        );
}


function formatParameterValue(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "-";
    }


    if (
        typeof value ===
        "object"
    ) {

        try {

            return JSON.stringify(
                value
            );

        } catch (_) {

            return String(
                value
            );
        }
    }


    return String(value);
}


function getRiskClass(
    score
) {

    if (
        score === null ||
        score === undefined ||
        score === "-"
    ) {

        return "";
    }


    const numericScore =
        Number(score);


    if (
        !Number.isFinite(
            numericScore
        )
    ) {

        return "";
    }


    if (
        numericScore >= 81
    ) {

        return "risk-critical";
    }


    if (
        numericScore >= 61
    ) {

        return "risk-high";
    }


    if (
        numericScore >= 31
    ) {

        return "risk-medium";
    }


    return "risk-low";
}


function formatAuditTimestamp(
    timestamp
) {

    if (!timestamp) {
        return "-";
    }


    const date =
        new Date(
            timestamp
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(
            timestamp
        );
    }


    return date.toLocaleString();
}


function escapeHtml(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


function capitalize(
    value
) {

    if (!value) {
        return "";
    }


    return String(value)
        .charAt(0)
        .toUpperCase() +
        String(value).slice(1);
}


// ============================================================
// REFRESH BUTTONS
// ============================================================

function setupRefreshButtons() {

    const dashboardRefresh =
        document.getElementById(
            "refreshBtn"
        );


    if (dashboardRefresh) {

        dashboardRefresh.addEventListener(
            "click",
            async () => {

                await loadDashboard();
            }
        );
    }
}


// ============================================================
// AUTOMATIC REFRESH
// ============================================================

function startAutoRefresh() {

    if (refreshTimer) {

        clearInterval(
            refreshTimer
        );
    }


    refreshTimer =
        setInterval(
            async () => {

                try {

                    if (
                        currentView ===
                        "dashboard"
                    ) {

                        await loadDashboard();

                    } else if (
                        currentView ===
                        "security"
                    ) {

                        await loadSecurityEvaluation();

                    } else if (
                        currentView ===
                        "approvals"
                    ) {

                        await loadApprovals();

                    } else if (
                        currentView ===
                        "audit"
                    ) {

                        await loadAuditLogs();
                    }

                } catch (error) {

                    console.error(
                        "[Auto Refresh] Error:",
                        error
                    );
                }

            },
            REFRESH_INTERVAL
        );
}


// ============================================================
// INITIALIZATION
// ============================================================

function initializeApp() {

    if (appInitialized) {
        return;
    }


    appInitialized =
        true;


    console.log(
        "================================================"
    );


    console.log(
        "Unified AI Governance Dashboard"
    );


    console.log(
        "Frontend initialized"
    );


    console.log(
        "================================================"
    );


    setupNavigation();


    setupRefreshButtons();


    currentView =
        "dashboard";


    setActiveNavigation(
        document.querySelectorAll(
            ".nav-item"
        ),
        "dashboard"
    );


    loadDashboard();


    startAutoRefresh();
}


// ============================================================
// DOM READY
// ============================================================

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeApp,
        {
            once: true
        }
    );

} else {

    initializeApp();
}