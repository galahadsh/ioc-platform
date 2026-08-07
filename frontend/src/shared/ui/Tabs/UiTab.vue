<template>
  <section
    v-show="isActive"
    :id="panelId"
    class="ui-tab-panel"
    role="tabpanel"
    :aria-labelledby="buttonId"
    tabindex="0"
  >
    <slot />
  </section>
</template>

<script setup>
import {
  computed,
  inject,
  onBeforeUnmount,
  onMounted,
} from "vue";

const props = defineProps({
  id: {
    type: String,
    required: true,
  },

  label: {
    type: String,
    required: true,
  },

  disabled: {
    type: Boolean,
    default: false,
  },
});

const context = inject(
  "uiTabsContext",
);

if (!context) {
  throw new Error(
    "UiTab debe utilizarse dentro de UiTabs.",
  );
}

const buttonId = computed(
  () => `ui-tab-${props.id}`,
);

const panelId = computed(
  () => `ui-tab-panel-${props.id}`,
);

const isActive = computed(
  () =>
    context.activeTab.value ===
    props.id,
);

onMounted(() => {
  context.registerTab({
    id: props.id,
    label: props.label,
    disabled: props.disabled,
    buttonId: buttonId.value,
    panelId: panelId.value,
  });
});

onBeforeUnmount(() => {
  context.unregisterTab(
    props.id,
  );
});
</script>
