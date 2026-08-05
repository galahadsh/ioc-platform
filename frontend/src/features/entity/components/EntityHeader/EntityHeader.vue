<template>

<header class="entity-header">

    <div>

        <div class="entity-header__type">

            {{ type }}

        </div>

        <div class="entity-header__title">

            {{ title }}

        </div>

        <div
            v-if="subtitle"
            class="entity-header__subtitle"
        >

            {{ subtitle }}

        </div>

        <div class="entity-header__meta">

            <StatusBadge
                :status="status"
            />

            <UiButton
                variant="ghost"
                size="sm"
            >

                {{ provider }}

            </UiButton>

        </div>

    </div>

</header>

</template>

<script setup>

import UiButton
from "@/shared/ui/Button";

import StatusBadge
from "@/shared/ui/StatusBadge";

import "./EntityHeader.css";

defineProps({

    type:{

        type:String,

        default:"IOC"

    },

    title:{

        type:String,

        required:true

    },

    subtitle:String,

    status:{

        type:String,

        default:"analizado"

    },

    provider:{

        type:String,

        default:"VirusTotal"

    }

});

</script>
