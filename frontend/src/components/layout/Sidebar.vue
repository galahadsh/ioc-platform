<template>

<aside class="sidebar">

    <div class="logo">

        <div class="logo-icon">
            🛡
        </div>

        <div>

            <div class="logo-title">
                IOC Platform
            </div>

            <div class="logo-subtitle">
                Enterprise
            </div>

        </div>

    </div>

    <div class="section">

        GENERAL

    </div>

    <RouterLink to="/">

        📊 Dashboard

    </RouterLink>

    <div class="section">

        THREAT INTELLIGENCE

    </div>

    <RouterLink to="/explorer">

        🔎 IOC Explorer

    </RouterLink>

    <RouterLink to="/campaigns">

        🎯 Campaigns

    </RouterLink>

    <RouterLink to="/malware">

        🦠 Malware

    </RouterLink>

    <RouterLink to="/actors">

        👤 Threat Actors

    </RouterLink>

    <div class="section">

        OPERATIONS

    </div>

    <RouterLink to="/cases">

        📁 Cases

    </RouterLink>

    <RouterLink to="/reports">

        📑 Reports

    </RouterLink>

    <div class="footer">

        Version 1.0 Alpha

    </div>

</aside>

</template>

<script setup>

</script>

<style scoped>

.sidebar{

    display:flex;

    flex-direction:column;

    background:#111827;

    min-height:100vh;

    padding:25px;

    gap:8px;

}

.logo{

    display:flex;

    gap:12px;

    align-items:center;

    margin-bottom:30px;

}

.logo-icon{

    width:48px;

    height:48px;

    border-radius:12px;

    background:#3B82F6;

    display:flex;

    justify-content:center;

    align-items:center;

    font-size:22px;

}

.logo-title{

    color:white;

    font-size:18px;

    font-weight:bold;

}

.logo-subtitle{

    color:#94A3B8;

    font-size:12px;

}

.section{

    margin-top:20px;

    margin-bottom:8px;

    color:#64748B;

    font-size:11px;

    font-weight:bold;

    letter-spacing:1px;

}

a{

    color:#CBD5E1;

    text-decoration:none;

    padding:12px;

    border-radius:8px;

    transition:.2s;

    font-size:14px;

}

a:hover{

    background:#1F2937;

}

.router-link-active{

    background:#2563EB;

    color:white;

}

.footer{

    margin-top:auto;

    color:#64748B;

    font-size:12px;

}

</style>