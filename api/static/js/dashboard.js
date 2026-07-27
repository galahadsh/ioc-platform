import {
    getStats,
    getMaliciousIOCs
} from "./api.js";

export async function cargarDashboard() {

    try {

        const stats = await getStats();

        document.getElementById("total").textContent =
            stats.total_iocs;

        document.getElementById("maliciosos").textContent =
            stats.maliciosos;

        document.getElementById("sospechosos").textContent =
            stats.sospechosos;

        document.getElementById("limpios").textContent =
            stats.limpios;


        const iocs = await getMaliciousIOCs();

        const tabla =
            document.getElementById("tabla");

        tabla.innerHTML = "";

        iocs.forEach(ioc => {

            tabla.innerHTML += `
                <tr>
                    <td>${ioc.tipo}</td>
                    <td>${ioc.valor}</td>
                    <td>${ioc.malicious}</td>
                    <td>${ioc.suspicious}</td>
                    <td>${ioc.proveedor}</td>
                    <td>${ioc.estado}</td>
                </tr>
            `;

        });

    } catch (error) {

        console.error(error);

    }

}