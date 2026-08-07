<template>

<EntitySection title="VirusTotal">

    <div class="vt-card">

        <div class="vt-score">

            <div>

                <div class="vt-score__label">

                    Score VT

                </div>

                <div class="vt-score__value">

                    {{ data.vt_score ?? 0 }}

                </div>

            </div>

            <StatusBadge
                :status="data.vt_estado"
            />

        </div>

        <div class="vt-grid">

            <div class="vt-item vt-item--malicious">

                <div class="vt-item__label">

                    Malicious

                </div>

                <div class="vt-item__value">

                    {{ data.vt_malicious }}

                </div>

            </div>

            <div class="vt-item vt-item--suspicious">

                <div class="vt-item__label">

                    Suspicious

                </div>

                <div class="vt-item__value">

                    {{ data.vt_suspicious }}

                </div>

            </div>

            <div class="vt-item vt-item--harmless">

                <div class="vt-item__label">

                    Harmless

                </div>

                <div class="vt-item__value">

                    {{ data.vt_harmless }}

                </div>

            </div>

            <div class="vt-item vt-item--undetected">

                <div class="vt-item__label">

                    Undetected

                </div>

                <div class="vt-item__value">

                    {{ data.vt_undetected }}

                </div>

            </div>

        </div>

        <EntityField
            label="Última consulta"
            :value="data.ultima_consulta"
        />

    </div>

</EntitySection>

</template>

<script setup>

import EntitySection from "../EntitySection";
import EntityField from "../EntityField";

import StatusBadge from "@/shared/ui/StatusBadge";

import "./VirusTotalCard.css";

defineProps({

    data:{

        type:Object,

        required:true

    }

});

</script>
