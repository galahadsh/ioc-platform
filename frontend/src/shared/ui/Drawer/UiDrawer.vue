<template>
  <Teleport to="body">
    <Transition name="ui-drawer">
      <div
        v-if="modelValue"
        class="ui-drawer-overlay"
        :class="
          `ui-drawer-overlay--${side}`
        "
        role="presentation"
        @mousedown.self="handleOverlayClick"
      >
        <aside
          ref="drawerElement"
          class="ui-drawer"
          :class="`ui-drawer--${side}`"
          :style="drawerStyle"
          role="dialog"
          aria-modal="true"
          :aria-label="title || 'Panel lateral'"
          tabindex="-1"
          @keydown="handleKeydown"
        >
          <header class="ui-drawer__header">
            <div class="ui-drawer__heading">
              <slot name="header">
                <h2
                  v-if="title"
                  class="ui-drawer__title"
                >
                  {{ title }}
                </h2>

                <p
                  v-if="subtitle"
                  class="ui-drawer__subtitle"
                >
                  {{ subtitle }}
                </p>
              </slot>
            </div>

            <button
              v-if="closable"
              type="button"
              class="ui-drawer__close"
              aria-label="Cerrar panel"
              @click="close"
            >
              ✕
            </button>
          </header>

          <section class="ui-drawer__body">
            <slot />
          </section>

          <footer
            v-if="$slots.footer"
            class="ui-drawer__footer"
          >
            <slot name="footer" />
          </footer>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  watch,
  ref,
} from "vue";

import "./UiDrawer.css";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },

  title: {
    type: String,
    default: "",
  },

  subtitle: {
    type: String,
    default: "",
  },

  side: {
    type: String,
    default: "right",
    validator: (value) =>
      ["left", "right"].includes(value),
  },

  width: {
    type: [
      String,
      Number,
    ],
    default: 520,
  },

  closable: {
    type: Boolean,
    default: true,
  },

  closeOnOverlay: {
    type: Boolean,
    default: true,
  },

  closeOnEscape: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "open",
  "close",
]);

const drawerElement = ref(null);

const drawerStyle = computed(() => {
  const normalizedWidth =
    typeof props.width === "number"
      ? `${props.width}px`
      : props.width;

  return {
    "--ui-drawer-width":
      normalizedWidth,
  };
});

function close() {
  emit(
    "update:modelValue",
    false,
  );

  emit("close");
}

function handleOverlayClick() {
  if (props.closeOnOverlay) {
    close();
  }
}

function getFocusableElements() {
  if (!drawerElement.value) {
    return [];
  }

  return Array.from(
    drawerElement.value.querySelectorAll(
      [
        "a[href]",
        "button:not([disabled])",
        "input:not([disabled])",
        "select:not([disabled])",
        "textarea:not([disabled])",
        '[tabindex]:not([tabindex="-1"])',
      ].join(","),
    ),
  );
}

function handleKeydown(event) {
  if (
    event.key === "Escape" &&
    props.closeOnEscape
  ) {
    event.preventDefault();
    close();
    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusable =
    getFocusableElements();

  if (!focusable.length) {
    event.preventDefault();
    drawerElement.value?.focus();
    return;
  }

  const first = focusable[0];
  const last =
    focusable[
      focusable.length - 1
    ];

  if (
    event.shiftKey &&
    document.activeElement === first
  ) {
    event.preventDefault();
    last.focus();
  } else if (
    !event.shiftKey &&
    document.activeElement === last
  ) {
    event.preventDefault();
    first.focus();
  }
}

function lockBodyScroll() {
  document.body.style.overflow =
    "hidden";
}

function unlockBodyScroll() {
  document.body.style.overflow = "";
}

watch(
  () => props.modelValue,
  async (isOpen) => {
    if (isOpen) {
      lockBodyScroll();

      await nextTick();

      drawerElement.value?.focus();

      emit("open");
    } else {
      unlockBodyScroll();
    }
  },
  {
    immediate: true,
  },
);

onBeforeUnmount(() => {
  unlockBodyScroll();
});
</script>
