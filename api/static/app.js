

async function subirArchivo(){


    let archivo =
    document.getElementById("archivo").files[0];


    if(!archivo){

        alert("Selecciona un archivo CSV");

        return;

    }



    let form = new FormData();

    form.append(
        "file",
        archivo
    );



    let respuesta =
    await fetch(
        "/api/upload",
        {
            method:"POST",
            body:form
        }
    );



    let resultado =
    await respuesta.json();



    document.getElementById("resultado").innerHTML =
    "Carga completada - Analysis ID: "
    + resultado.analysis_id
    + " IOC cargados: "
    + resultado.iocs_cargados;



    cargarDashboard();

    cargarHistorial();


}





async function cargarDashboard(){


let stats =
await fetch("/api/stats");


let data =
await stats.json();



document.getElementById("total").innerHTML =
data.total_iocs;


document.getElementById("maliciosos").innerHTML =
data.maliciosos;


document.getElementById("sospechosos").innerHTML =
data.sospechosos;


document.getElementById("limpios").innerHTML =
data.limpios;



let response =
await fetch("/api/iocs/malicious");


let iocs =
await response.json();



let tabla =
document.getElementById("tabla");


tabla.innerHTML="";



iocs.forEach(i=>{


tabla.innerHTML += `

<tr>

<td>${i.tipo}</td>

<td>${i.valor}</td>

<td>${i.malicious}</td>

<td>${i.suspicious}</td>

<td>${i.proveedor}</td>

<td>${i.estado}</td>


</tr>

`;


});


}





async function cargarHistorial(){


let response =
await fetch("/api/analysis/history");


let data =
await response.json();



let tabla =
document.getElementById("historial");


tabla.innerHTML="";



data.forEach(a=>{


tabla.innerHTML += `

<tr>

<td>${a.id}</td>

<td>${a.archivo}</td>

<td>${a.estado}</td>

<td>${a.total_iocs}</td>

<td>${a.maliciosos}</td>

<td>${a.fecha_inicio}</td>

</tr>


`;


});


}



cargarDashboard();

cargarHistorial();

