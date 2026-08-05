<template>

<div class="ui-card">

    <header
        v-if="$slots.header || title"
        class="ui-card-header"
    >

        <div>

            <div
                v-if="title"
                class="ui-card-title"
            >

                {{ title }}

            </div>

            <div
                v-if="subtitle"
                class="ui-card-subtitle"
            >

                {{ subtitle }}

            </div>

            <slot
                name="header"
            />

        </div>

        <slot
            name="actions"
        />

    </header>

    <section class="ui-card-body">

        <slot />

    </section>

    <footer
        v-if="$slots.footer"
        class="ui-card-footer"
    >

        <slot
            name="footer"
        />

    </footer>

</div>

</template>

<script setup>

import "./UiCard.css";

defineProps({

    title:String,

    subtitle:String

});

</script>
