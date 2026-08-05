const routeTitles = {
    "/enterprise/dashboard": "Dashboard",
    "/enterprise/explorer": "IOC Explorer",
    "/enterprise/campaigns": "Campaigns",
    "/enterprise/malware": "Malware",
    "/enterprise/actors": "Threat Actors",
    "/enterprise/hunting": "Threat Hunting",
    "/enterprise/cases": "Cases",
    "/enterprise/reports": "Reports"
};


function currentRoute() {
    return (
        window.location.hash.replace(
            "#",
            ""
        ) ||
        "/enterprise/dashboard"
    );
}


function synchronizeNavigation() {
    const route = currentRoute();

    document
        .querySelectorAll(
            ".enterprise-nav-link"
        )
        .forEach((link) => {
            const linkRoute =
                link.getAttribute("href")
                    ?.replace("#", "");

            link.classList.toggle(
                "is-active",
                linkRoute === route
            );
        });

    const title =
        document.getElementById(
            "enterprise-page-title"
        );

    if (title) {
        title.textContent =
            routeTitles[route] ??
            "IOC Platform";
    }
}


window.addEventListener(
    "hashchange",
    synchronizeNavigation
);


document.addEventListener(
    "DOMContentLoaded",
    synchronizeNavigation
);


console.log(
    "IOC Platform Enterprise UI cargada."
);
