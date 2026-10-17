<template>
  <div class="homepage-cards-editor pl-6">
    <div class="d-flex align-center mb-2">
      <v-icon small class="mr-2">mdi-view-grid-outline</v-icon>
      <span class="text-body-1">{{ $t("settings.homepage_builtin") }}</span>
    </div>
    <v-list dense class="homepage-section-list">
      <v-list-item
        v-for="(section, idx) in local.order"
        :key="section"
        class="px-0"
        :class="{ 'homepage-section-drag-over': dragOverSection === section }"
        @dragover.prevent.native="onSectionDragOver(section)"
        @drop.prevent.native="onSectionDrop(section)"
      >
        <v-list-item-action class="mr-1">
          <v-icon
            small
            class="homepage-section-handle"
            draggable="true"
            @click.stop
            @dragstart.native="onSectionDragStart(section, $event)"
            @dragend.native="onSectionDragEnd"
          >mdi-drag</v-icon>
        </v-list-item-action>
        <v-list-item-action class="mr-2">
          <v-checkbox
            :input-value="isEnabled(section)"
            hide-details
            dense
            class="mt-0"
            @change="toggleSection(section)"
          ></v-checkbox>
        </v-list-item-action>
        <v-list-item-icon class="mr-2">
          <v-icon small>{{ sectionIcon(section) }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>{{ sectionTitle(section) }}</v-list-item-title>
        </v-list-item-content>
        <v-list-item-action class="d-flex flex-row">
          <v-btn icon x-small :disabled="idx === 0" @click="moveSection(section, -1)">
            <v-icon small>mdi-chevron-up</v-icon>
          </v-btn>
          <v-btn icon x-small :disabled="idx === local.order.length - 1" @click="moveSection(section, 1)">
            <v-icon small>mdi-chevron-down</v-icon>
          </v-btn>
        </v-list-item-action>
      </v-list-item>
    </v-list>

    <div class="d-flex align-center mt-4 mb-2">
      <v-icon small class="mr-2">mdi-card-plus-outline</v-icon>
      <span class="text-body-1">{{ $t("settings.homepage_custom") }}</span>
      <v-spacer></v-spacer>
      <v-btn small color="primary" text @click="addCard">
        <v-icon left small>mdi-plus</v-icon>{{ $t("settings.homepage_add_card") }}
      </v-btn>
    </div>

    <p v-if="local.custom.length === 0" class="grey--text text-body-2">
      {{ $t("settings.homepage_custom_empty") }}
    </p>

    <v-card
      v-for="card in local.custom"
      :key="card.id"
      outlined
      class="homepage-custom-card mb-3"
    >
      <v-card-text class="pb-2">
        <v-row dense>
          <v-col cols="12" sm="4">
            <v-select
              v-model="card.type"
              :items="typeOptions"
              :label="$t('settings.homepage_card_type')"
              dense
              outlined
              hide-details
              @change="onTypeChange(card)"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="8">
            <v-combobox
              v-if="card.type === 'author' || card.type === 'tag' || card.type === 'series'"
              v-model="card.value"
              :items="valueItems(card)"
              :label="$t('settings.homepage_card_value')"
              dense
              outlined
              hide-details
              clearable
              @update:search-input="(q) => onValueSearch(card, q)"
            ></v-combobox>
            <v-select
              v-else-if="card.type === 'language'"
              v-model="card.value"
              :items="languageItems"
              :label="$t('settings.homepage_card_value')"
              dense
              outlined
              hide-details
            ></v-select>
            <v-select
              v-else
              v-model="card.value"
              :items="ratingItems"
              :label="$t('settings.homepage_card_value')"
              dense
              outlined
              hide-details
            ></v-select>
          </v-col>
          <v-col cols="6" sm="4">
            <v-select
              v-model="card.sort"
              :items="sortOptions(card)"
              :label="$t('settings.homepage_card_sort')"
              dense
              outlined
              hide-details
            ></v-select>
          </v-col>
          <v-col cols="6" sm="4">
            <v-select
              v-model="card.limit"
              :items="limitOptions"
              :label="$t('settings.homepage_card_limit')"
              dense
              outlined
              hide-details
            ></v-select>
          </v-col>
          <v-col cols="12" sm="2" class="d-flex align-center justify-end">
            <v-btn icon small color="error" @click="removeCard(card)">
              <v-icon small>mdi-delete-outline</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <p class="text-caption grey--text mt-2">
      {{ $t("settings.homepage_order_hint") }}
    </p>
  </div>
</template>

<script>
import {
  BUILTIN_SECTIONS,
  CUSTOM_LIMITS,
  CUSTOM_SORTS,
  CUSTOM_TYPES,
  SECTION_META,
  cardSectionKey,
  defaultSortFor,
  normalizeHomepageConfig,
  sectionLabel,
} from "~/utils/homepage";

const TYPE_ICONS = {
  author: "mdi-account-outline",
  tag: "mdi-tag-outline",
  series: "mdi-bookshelf",
  language: "mdi-translate",
  rating: "mdi-star-outline",
};

export default {
  name: "HomepageCardsEditor",
  props: {
    value: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      local: normalizeHomepageConfig(this.value),
      emitting: false,
      dragSection: null,
      dragOverSection: null,
      authorItems: [],
      tagItems: [],
      seriesItems: [],
      languageItems: [],
      searchTimers: {},
    };
  },
  computed: {
    typeOptions() {
      return CUSTOM_TYPES.map((type) => ({
        value: type,
        text: this.$t("settings.homepage_type_" + type),
      }));
    },
    limitOptions() {
      return CUSTOM_LIMITS.map((value) => ({ value, text: String(value) }));
    },
    ratingItems() {
      return [1, 2, 3, 4, 5].map((value) => ({
        value: String(value),
        text: this.$t("settings.homepage_rating_value", { n: value }),
      }));
    },
  },
  watch: {
    value: {
      deep: true,
      handler(val) {
        if (this.emitting) return;
        const normalized = normalizeHomepageConfig(val);
        if (JSON.stringify(normalized) !== JSON.stringify(this.local)) {
          this.local = normalized;
        }
      },
    },
    local: {
      deep: true,
      handler(val) {
        if (JSON.stringify(val) === JSON.stringify(this.value)) return;
        this.emitting = true;
        this.$emit("input", JSON.parse(JSON.stringify(val)));
        this.$nextTick(() => {
          this.emitting = false;
        });
      },
    },
  },
  mounted() {
    this.loadSeries();
    this.loadLanguages();
  },
  beforeDestroy() {
    Object.keys(this.searchTimers).forEach((key) => clearTimeout(this.searchTimers[key]));
  },
  methods: {
    sectionTitle(section) {
      if (BUILTIN_SECTIONS.includes(section)) {
        const meta = SECTION_META[section];
        return meta ? this.$t(meta.label) : section;
      }
      const card = this.cardForSection(section);
      return card ? sectionLabel(card, (key, params) => this.$t(key, params)) : section;
    },
    sectionIcon(section) {
      if (BUILTIN_SECTIONS.includes(section)) {
        const meta = SECTION_META[section];
        return meta ? meta.icon : "mdi-view-grid-outline";
      }
      const card = this.cardForSection(section);
      return card ? TYPE_ICONS[card.type] || "mdi-card-outline" : "mdi-card-outline";
    },
    cardForSection(section) {
      if (!section.startsWith("custom:")) return null;
      const id = section.slice("custom:".length);
      return this.local.custom.find((card) => card.id === id) || null;
    },
    isEnabled(section) {
      return !this.local.hidden.includes(section);
    },
    toggleSection(section) {
      if (this.isEnabled(section)) {
        this.local.hidden = this.local.hidden.concat([section]);
      } else {
        this.local.hidden = this.local.hidden.filter((item) => item !== section);
      }
    },
    moveSection(section, delta) {
      const from = this.local.order.indexOf(section);
      const to = from + delta;
      if (from < 0 || to < 0 || to >= this.local.order.length) return;
      const order = this.local.order.slice();
      order.splice(from, 1);
      order.splice(to, 0, section);
      this.local.order = order;
    },
    onSectionDragStart(section, event) {
      this.dragSection = section;
      if (event && event.dataTransfer) {
        event.dataTransfer.effectAllowed = "move";
        event.dataTransfer.setData("text/plain", section);
      }
    },
    onSectionDragOver(section) {
      if (this.dragSection && this.dragSection !== section) {
        this.dragOverSection = section;
      }
    },
    onSectionDrop(section) {
      const from = this.local.order.indexOf(this.dragSection);
      const to = this.local.order.indexOf(section);
      if (from === -1 || to === -1 || from === to) {
        this.onSectionDragEnd();
        return;
      }
      const order = this.local.order.slice();
      order.splice(from, 1);
      order.splice(to, 0, this.dragSection);
      this.local.order = order;
      this.onSectionDragEnd();
    },
    onSectionDragEnd() {
      this.dragSection = null;
      this.dragOverSection = null;
    },
    onTypeChange(card) {
      card.value = "";
      card.sort = defaultSortFor(card.type);
    },
    sortOptions(card) {
      return CUSTOM_SORTS.filter((sort) => sort !== "series" || card.type === "series").map((sort) => ({
        value: sort,
        text: this.$t("settings.homepage_sort_" + sort),
      }));
    },
    valueItems(card) {
      if (card.type === "tag") return this.tagItems;
      if (card.type === "series") return this.seriesItems;
      return this.authorItems;
    },
    onValueSearch(card, query) {
      if (!query || query.length < 1) return;
      if (card.type !== "author" && card.type !== "tag") return;
      const key = card.type;
      if (this.searchTimers[key]) clearTimeout(this.searchTimers[key]);
      this.searchTimers[key] = setTimeout(() => {
        const url = card.type === "author"
          ? "/authors/search?limit=30&q=" + encodeURIComponent(query)
          : "/tags/search?limit=30&q=" + encodeURIComponent(query);
        this.$backend(url).then((rsp) => {
          if (rsp.err !== "ok") return;
          const items = card.type === "author" ? rsp.authors : rsp.tags;
          const names = (items || []).map((item) => item.name);
          if (card.type === "author") this.authorItems = names;
          else this.tagItems = names;
        });
      }, 300);
    },
    loadSeries() {
      this.$backend("/series?show=all").then((rsp) => {
        if (rsp.err === "ok") this.seriesItems = (rsp.items || []).map((item) => item.name);
      });
    },
    loadLanguages() {
      this.$backend("/language?show=all").then((rsp) => {
        if (rsp.err === "ok") this.languageItems = (rsp.items || []).map((item) => item.name);
      });
    },
    addCard() {
      const id = "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      this.local.custom = this.local.custom.concat([
        {
          id,
          type: "author",
          value: "",
          sort: "new",
          limit: 12,
        },
      ]);
      this.local.order = this.local.order.concat([cardSectionKey({ id })]);
    },
    removeCard(card) {
      const section = cardSectionKey(card);
      this.local.custom = this.local.custom.filter((item) => item.id !== card.id);
      this.local.order = this.local.order.filter((item) => item !== section);
      this.local.hidden = this.local.hidden.filter((item) => item !== section);
    },
  },
};
</script>

<style scoped>
.homepage-section-list {
  background: transparent;
}

.homepage-section-handle {
  cursor: grab;
}

.homepage-section-handle:active {
  cursor: grabbing;
}

.homepage-section-drag-over {
  outline: 2px dashed #1976d2;
  outline-offset: -2px;
}

.homepage-custom-card {
  border-radius: 8px;
}
</style>
