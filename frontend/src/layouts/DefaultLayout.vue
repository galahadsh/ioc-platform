<template>

<div class="layout">

    <Sidebar />

    <div class="main">

        <Header />

        <main class="content">

            <RouterView />

        </main>

    </div>

</div>

</template>

<script setup>

import Sidebar from "../components/layout/Sidebar.vue";
import Header from "../components/layout/Header.vue";

</script>

<style scoped>

.layout{

    display:grid;

    grid-template-columns:250px 1fr;

    min-height:100vh;

    background:#09111B;

}

.main{

    display:flex;

    flex-direction:column;

}

.content{

    flex:1;

    overflow:auto;

}

</style>