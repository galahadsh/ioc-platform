<template>
  <div class="ui-tabs">
    <div
      ref="tabListElement"
      class="ui-tabs__header"
      role="tablist"
      :aria-label="ariaLabel"
      @keydown="handleKeydown"
    >
      <button
        v-for="tab in tabs"
        :id="tab.buttonId"
        :key="tab.id"
        type="button"
        class="ui-tabs__button"
        :class="{
          'ui-tabs__button--active':
            tab.id === activeTab,
        }"
        role="tab"
        :aria-selected="
          tab.id === activeTab
        "
        :aria-controls="tab.panelId"
        :tabindex="
          tab.id === activeTab
            ? 0
            : -1
        "
        :disabled="tab.disabled"
        @click="selectTab(tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="ui-tabs__content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import {
  nextTick,
  provide,
  ref,
} from "vue";

import "./UiTabs.css";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },

  ariaLabel: {
    type: String,
    default: "Pestañas",
  },
});

const emit = defineEmits([
  "update:modelValue",
  "change",
]);

const tabs = ref([]);
const activeTab = ref(
  props.modelValue,
);
const tabListElement = ref(null);

function registerTab(tab) {
  const exists = tabs.value.some(
    (currentTab) =>
      currentTab.id === tab.id,
  );

  if (!exists) {
    tabs.value.push(tab);
  }

  if (
    !activeTab.value &&
    !tab.disabled
  ) {
    selectTab(tab.id);
  }
}

function unregisterTab(tabId) {
  tabs.value = tabs.value.filter(
    (tab) => tab.id !== tabId,
  );

  if (activeTab.value !== tabId) {
    return;
  }

  const nextTab = tabs.value.find(
    (tab) => !tab.disabled,
  );

  if (nextTab) {
    selectTab(nextTab.id);
  } else {
    activeTab.value = "";
  }
}

function selectTab(tabId) {
  const tab = tabs.value.find(
    (currentTab) =>
      currentTab.id === tabId,
  );

  if (!tab || tab.disabled) {
    return;
  }

  activeTab.value = tabId;

  emit(
    "update:modelValue",
    tabId,
  );

  emit(
    "change",
    tabId,
  );
}

async function focusTab(tabId) {
  await nextTick();

  document
    .getElementById(
      tabs.value.find(
        (tab) => tab.id === tabId,
      )?.buttonId,
    )
    ?.focus();
}

function enabledTabs() {
  return tabs.value.filter(
    (tab) => !tab.disabled,
  );
}

async function handleKeydown(event) {
  if (
    ![
      "ArrowLeft",
      "ArrowRight",
      "Home",
      "End",
    ].includes(event.key)
  ) {
    return;
  }

  event.preventDefault();

  const availableTabs =
    enabledTabs();

  if (!availableTabs.length) {
    return;
  }

  const currentIndex =
    availableTabs.findIndex(
      (tab) =>
        tab.id === activeTab.value,
    );

  let nextIndex = currentIndex;

  if (event.key === "ArrowRight") {
    nextIndex =
      currentIndex >=
      availableTabs.length - 1
        ? 0
        : currentIndex + 1;
  }

  if (event.key === "ArrowLeft") {
    nextIndex =
      currentIndex <= 0
        ? availableTabs.length - 1
        : currentIndex - 1;
  }

  if (event.key === "Home") {
    nextIndex = 0;
  }

  if (event.key === "End") {
    nextIndex =
      availableTabs.length - 1;
  }

  const nextTab =
    availableTabs[nextIndex];

  selectTab(nextTab.id);
  await focusTab(nextTab.id);
}

provide(
  "uiTabsContext",
  {
    activeTab,
    registerTab,
    unregisterTab,
  },
);
</script>
