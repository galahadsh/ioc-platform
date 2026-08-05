<template>
    <header class="header">

        <div class="header-left">

            <div class="page-title">
                IOC Platform Enterprise
            </div>

            <div class="breadcrumb">
                Cyber Threat Intelligence
            </div>

        </div>

        <div class="header-center">

            <input
                class="search"
                type="text"
                placeholder="Buscar IOC, Campaign, Malware..."
            >

        </div>

        <div class="header-right">

            <button class="icon-button">
                🔄
            </button>

            <button class="icon-button">
                🔔
            </button>

            <div class="user">

                <div class="avatar">
                    FG
                </div>

                <div>

                    <div class="user-name">
                        Fernando
                    </div>

                    <div class="user-role">
                        CTI Manager
                    </div>

                </div>

            </div>

        </div>

    </header>
</template>

<script setup>
</script>

<style scoped>

.header{

    display:flex;

    justify-content:space-between;

    align-items:center;

    height:72px;

    padding:0 28px;

    background:#162131;

    border-bottom:1px solid #223449;

}

.header-left{

    display:flex;

    flex-direction:column;

}

.page-title{

    color:white;

    font-size:22px;

    font-weight:700;

}

.breadcrumb{

    color:#8CA0B3;

    font-size:12px;

}

.header-center{

    flex:1;

    display:flex;

    justify-content:center;

}

.search{

    width:420px;

    padding:10px 15px;

    border:none;

    border-radius:8px;

    background:#0D1725;

    color:white;

    outline:none;

}

.search::placeholder{

    color:#607386;

}

.header-right{

    display:flex;

    align-items:center;

    gap:18px;

}

.icon-button{

    width:40px;

    height:40px;

    border:none;

    border-radius:8px;

    background:#0D1725;

    color:white;

    cursor:pointer;

    transition:.2s;

}

.icon-button:hover{

    background:#1D2E45;

}

.user{

    display:flex;

    align-items:center;

    gap:10px;

}

.avatar{

    width:42px;

    height:42px;

    border-radius:50%;

    display:flex;

    justify-content:center;

    align-items:center;

    background:#3B82F6;

    color:white;

    font-weight:bold;

}

.user-name{

    color:white;

    font-size:14px;

    font-weight:600;

}

.user-role{

    color:#8CA0B3;

    font-size:12px;

}

</style>