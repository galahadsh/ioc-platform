const routes = {
    "/dashboard": {
        view: "/static/views/dashboard.html",
        module: "dashboard"
    },

    "/explorer": {
        view: "/static/views/explorer.html",
        module: "explorer"
    },

    "/analysis": {
        view: "/static/views/analysis.html",
        module: "analysis"
    },

    "/threat-intelligence/dashboard": {
        view: "/static/views/threat-intelligence/dashboard.html",
        module: "threat-dashboard"
    },

    "/threat-intelligence/statistics": {
        view: "/static/views/threat-intelligence/statistics.html",
        module: "statistics"
    },

    "/threat-intelligence/campaigns": {
        view: "/static/views/threat-intelligence/campaigns.html",
        module: "campaigns"
    },

    "/threat-intelligence/malware": {
        view: "/static/views/threat-intelligence/malware.html",
        module: "malware"
    },

    "/threat-intelligence/actors": {
        view: "/static/views/threat-intelligence/actors.html",
        module: "actors"
    },

    "/threat-intelligence/sources": {
        view: "/static/views/threat-intelligence/sources.html",
        module: "sources"
    },

    "/threat-intelligence/feeds": {
        view: "/static/views/threat-intelligence/feeds.html",
        module: "feeds"
    },

    "/hunting": {
        view: "/static/views/hunting.html",
        module: "hunting"
    },

    "/reports": {
        view: "/static/views/reports.html",
        module: "reports"
    },

    "/integrations": {
        view: "/static/views/integrations.html",
        module: "integrations"
    },

    "/settings": {
        view: "/static/views/settings.html",
        module: "settings"
    }
};


function normalizeRoute() {
    const hash = window.location.hash.replace(/^#/, "");

    if (!hash || hash === "/") {
        return "/dashboard";
    }

    return hash;
}


function setActiveNavigation(route) {
    document
        .querySelectorAll(".nav-link")
        .forEach((link) => {
            const isActive =
                link.dataset.route === route;

            link.classList.toggle(
                "active",
                isActive
            );
        });

    if (route.startsWith("/threat-intelligence/")) {
        openThreatIntelligenceMenu();
    }
}


function setLoading(isLoading) {
    const loading = document.getElementById(
        "view-loading"
    );

    if (loading) {
        loading.hidden = !isLoading;
    }
}


function showError(message) {
    const error = document.getElementById(
        "view-error"
    );

    if (!error) {
        return;
    }

    error.textContent = message;
    error.hidden = false;
}


function hideError() {
    const error = document.getElementById(
        "view-error"
    );

    if (!error) {
        return;
    }

    error.textContent = "";
    error.hidden = true;
}


export function openThreatIntelligenceMenu() {
    const toggle = document.getElementById(
        "threat-intelligence-toggle"
    );

    const submenu = document.getElementById(
        "threat-intelligence-submenu"
    );

    if (!toggle || !submenu) {
        return;
    }

    submenu.hidden = false;
    toggle.setAttribute(
        "aria-expanded",
        "true"
    );

    toggle.classList.add("expanded");
}


function toggleThreatIntelligenceMenu() {
    const toggle = document.getElementById(
        "threat-intelligence-toggle"
    );

    const submenu = document.getElementById(
        "threat-intelligence-submenu"
    );

    if (!toggle || !submenu) {
        return;
    }

    const isExpanded =
        toggle.getAttribute("aria-expanded") === "true";

    toggle.setAttribute(
        "aria-expanded",
        String(!isExpanded)
    );

    toggle.classList.toggle(
        "expanded",
        !isExpanded
    );

    submenu.hidden = isExpanded;
}


export async function loadCurrentRoute() {
    let route = normalizeRoute();

    if (!routes[route]) {
        route = "/dashboard";
        window.location.hash = route;
        return;
    }

    const routeConfig = routes[route];
    const viewContainer =
        document.getElementById("app-view");

    if (!viewContainer) {
        return;
    }

    try {
        hideError();
        setLoading(true);

        const response = await fetch(
            routeConfig.view,
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                `No fue posible cargar la vista: ${response.status}`
            );
        }

        viewContainer.innerHTML =
            await response.text();

        setActiveNavigation(route);

        document.dispatchEvent(
            new CustomEvent(
                "iocplatform:view-loaded",
                {
                    detail: {
                        route,
                        module: routeConfig.module
                    }
                }
            )
        );

        window.scrollTo({
            top: 0,
            behavior: "instant"
        });

    } catch (error) {
        console.error(error);

        showError(
            "No fue posible cargar el módulo solicitado."
        );

    } finally {
        setLoading(false);
    }
}


export function initializeRouter() {
    document
        .getElementById(
            "threat-intelligence-toggle"
        )
        ?.addEventListener(
            "click",
            toggleThreatIntelligenceMenu
        );

    window.addEventListener(
        "hashchange",
        loadCurrentRoute
    );

    loadCurrentRoute();
}
