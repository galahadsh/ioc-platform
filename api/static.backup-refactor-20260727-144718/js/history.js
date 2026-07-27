import {
    getHistory
} from "./api.js";

export async function cargarHistorial() {

    try {

        const historial =
            await getHistory();

        const tabla =
            document.getElementById("historial");

        tabla.innerHTML = "";

        historial.forEach(item => {

            tabla.innerHTML += `
                <tr>
                    <td>${item.id}</td>
                    <td>${item.archivo}</td>
                    <td>${item.estado}</td>
                    <td>${item.total_iocs}</td>
                    <td>${item.maliciosos}</td>
                    <td>${item.fecha_inicio}</td>
                </tr>
            `;

        });

    } catch (error) {

        console.error(error);

    }

}