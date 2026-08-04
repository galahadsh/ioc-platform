<template>
    <div class="metric-card">

        <div class="metric-header">

            <span class="metric-title">
                {{ title }}
            </span>

            <span
                class="metric-icon"
                :class="color"
            >
                {{ icon }}
            </span>

        </div>

        <div class="metric-value">

            {{ value }}

        </div>

        <div class="metric-footer">

            <span
                class="trend"
                :class="color"
            >
                {{ trend }}
            </span>

        </div>

    </div>
</template>

<script setup>

defineProps({

    title: String,

    value: [String, Number],

    trend: {

        type: String,

        default: ""

    },

    icon: {

        type: String,

        default: "●"

    },

    color: {

        type: String,

        default: "blue"

    }

});

</script>

<style scoped>

.metric-card{

    background:#162131;

    border:1px solid #223449;

    border-radius:14px;

    padding:22px;

    display:flex;

    flex-direction:column;

    gap:18px;

    transition:.2s;

}

.metric-card:hover{

    transform:translateY(-3px);

    border-color:#3B82F6;

}

.metric-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

}

.metric-title{

    color:#8CA0B3;

    font-size:14px;

}

.metric-icon{

    font-size:18px;

}

.metric-value{

    font-size:42px;

    font-weight:700;

    color:white;

}

.metric-footer{

    font-size:13px;

}

.blue{

    color:#3B82F6;

}

.green{

    color:#22C55E;

}

.orange{

    color:#F59E0B;

}

.red{

    color:#EF4444;

}

</style>