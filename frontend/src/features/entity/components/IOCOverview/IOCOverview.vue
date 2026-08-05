<template>

<div>

    <EntityHeader
        type="IOC"
        :title="ioc.valor"
        :subtitle="ioc.tipo"
        :status="ioc.vt_estado"
        :provider="ioc.proveedor_reputacion"
    />

    <EntitySection title="Overview">

        <EntityField
            label="Tipo"
            :value="ioc.tipo"
        />

        <EntityField
            label="Fuente"
            :value="ioc.fuente"
        />

        <EntityField
            label="Campaña"
            :value="ioc.campaign"
        />

        <EntityField
            label="Malware"
            :value="ioc.malware_family"
        />

        <EntityField
            label="Fecha"
            :value="ioc.fecha_creacion"
        />

    </EntitySection>

</div>

</template>

<script setup>

import EntityHeader from "../EntityHeader";
import EntitySection from "../EntitySection";
import EntityField from "../EntityField";

defineProps({

    ioc:{
        type:Object,
        required:true
    }

});

</script>
