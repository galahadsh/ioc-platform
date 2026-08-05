<template>

<section class="entity-section">

    <header
        v-if="title"
        class="entity-section__title"
    >

        {{ title }}

    </header>

    <div class="entity-section__body">

        <slot/>

    </div>

</section>

</template>

<script setup>

import "./EntitySection.css";

defineProps({

    title:{

        type:String,

        default:""

    }

});

</script>
