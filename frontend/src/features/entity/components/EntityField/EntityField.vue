<template>

<div class="entity-field">

    <div class="entity-field__label">

        {{ label }}

    </div>

    <div
        class="entity-field__value"
        :class="{
            'entity-field__value--empty': displayValue==='—'
        }"
    >

        <slot>

            {{ displayValue }}

        </slot>

    </div>

</div>

</template>

<script setup>

import { computed } from "vue";

import "./EntityField.css";

const props = defineProps({

    label:{
        type:String,
        required:true
    },

    value:{
        type:[
            String,
            Number,
            Boolean
        ],
        default:null
    }

});

const displayValue=computed(()=>{

    if(
        props.value===null ||
        props.value===undefined ||
        props.value===""

    ){

        return "—";

    }

    return String(props.value);

});

</script>
