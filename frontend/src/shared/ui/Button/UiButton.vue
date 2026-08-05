<template>

<button

    class="ui-button"

    :class="[

        `ui-button--${variant}`,

        `ui-button--${size}`

    ]"

    :disabled="disabled || loading"

>

    <span

        v-if="loading"

        class="ui-button__spinner"

    />

    <slot

        name="icon"

        v-else

    />

    <slot />

</button>

</template>

<script setup>

import "./UiButton.css";

defineProps({

    variant:{

        type:String,

        default:"primary"

    },

    size:{

        type:String,

        default:"md"

    },

    loading:Boolean,

    disabled:Boolean

});

</script>
