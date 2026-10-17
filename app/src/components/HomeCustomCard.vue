<template>
  <home-section-card
    v-if="loading || books.length"
    :icon="icon"
    :title="title"
    :storage-key="'custom:' + card.id"
  >
    <template #header-extra>
      <v-btn x-small text color="primary" :to="viewAllLink" @click.stop>
        {{ $t("common.viewAll") }}
      </v-btn>
    </template>
    <v-row v-if="loading && books.length === 0">
      <v-col cols="4" xs="4" sm="3" md="2" lg="1" v-for="n in card.limit" :key="'custom-ph-' + n" class="book-card">
        <v-card class="ma-1">
          <div class="book-img-container">
            <v-skeleton-loader type="image" class="cover-fill-img"></v-skeleton-loader>
          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="4" xs="4" sm="3" md="2" lg="1" v-for="book in books" :key="'custom-' + card.id + '-' + book.id" class="book-card">
        <v-card :to="book.href" class="ma-1">
          <div class="book-img-container" :title="book.title">
            <v-img :src="book.thumb" class="cover-fill-img book-img-hover"></v-img>
            <div v-if="book.book_type === 1" class="physical-book-badge">
              <v-icon small color="white">mdi-bookshelf</v-icon>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </home-section-card>
</template>

<script>
import HomeSectionCard from "~/components/HomeSectionCard.vue";
import { customCardViewAll, defaultSortFor, sectionLabel } from "~/utils/homepage";

const ICONS = {
  author: "mdi-account-outline",
  tag: "mdi-tag-outline",
  series: "mdi-bookshelf",
  language: "mdi-translate",
  rating: "mdi-star-outline",
};

export default {
  name: "HomeCustomCard",
  components: { HomeSectionCard },
  props: {
    card: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      books: [],
      loading: false,
    };
  },
  computed: {
    icon() {
      return ICONS[this.card.type] || "mdi-card-outline";
    },
    title() {
      return sectionLabel(this.card, (key, params) => this.$t(key, params));
    },
    viewAllLink() {
      return customCardViewAll(this.card);
    },
  },
  watch: {
    card: {
      deep: true,
      handler() {
        this.loadBooks();
      },
    },
  },
  mounted() {
    this.loadBooks();
  },
  methods: {
    async loadBooks() {
      if (!this.card.value) {
        this.books = [];
        return;
      }
      const sort = this.card.sort || defaultSortFor(this.card.type);
      const value = encodeURIComponent(this.card.value);
      const url = `/${this.card.type}/${value}?size=${this.card.limit}&sort=${sort}&cover=1`;
      this.loading = true;
      try {
        const rsp = await this.$backend(url);
        if (rsp.err === "ok") {
          this.books = (rsp.books || []).map((book) => {
            book.href = "/book/" + book.id;
            return book;
          });
        } else {
          this.books = [];
        }
      } catch (error) {
        this.books = [];
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
