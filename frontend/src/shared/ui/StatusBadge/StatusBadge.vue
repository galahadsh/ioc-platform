<template>

<span
    class="ui-status-badge"
    :class="badgeClass"
>

    <span
        class="ui-status-badge__dot"
    />

    {{ label }}

</span>

</template>

<script setup>

import { computed } from "vue";

import "./StatusBadge.css";

const props = defineProps({

    status:{

        type:String,

        default:"unknown"

    }

});

const map={

    analizado:{
        label:"Analizado",
        class:"success"
    },

    malicious:{
        label:"Malicioso",
        class:"danger"
    },

    malicioso:{
        label:"Malicioso",
        class:"danger"
    },

    suspicious:{
        label:"Sospechoso",
        class:"warning"
    },

    harmless:{
        label:"Limpio",
        class:"success"
    },

    clean:{
        label:"Limpio",
        class:"success"
    },

    pendiente:{
        label:"Pendiente",
        class:"info"
    },

    pending:{
        label:"Pendiente",
        class:"info"
    },

    error:{
        label:"Error",
        class:"danger"
    }

};

const current=computed(()=>{

    return map[
        props.status?.toLowerCase()
    ]??{

        label:props.status,

        class:"neutral"

    };

});

const label=computed(()=>current.value.label);

const badgeClass=computed(()=>

`ui-status-badge--${current.value.class}`

);

</script>
