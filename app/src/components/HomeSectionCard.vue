<template>
    <div
        class="home-section-card"
        :class="{ 'home-section-card--collapsed': !expanded }"
    >
        <v-row>
            <v-col cols="12">
                <div
                    class="d-flex align-center home-section-card-header"
                    :title="expanded ? $t('common.collapse') : $t('common.expand')"
                    @click="toggle"
                >
                    <v-icon small class="mr-1">{{ icon }}</v-icon>
                    <p class="ma-0">{{ title }}</p>
                    <span @click.stop><slot name="header-extra"></slot></span>
                    <v-spacer></v-spacer>
                    <v-icon class="home-section-card-toggle">{{ expanded ? 'mdi-chevron-down' : 'mdi-chevron-right' }}</v-icon>
                </div>
            </v-col>
        </v-row>
        <v-expand-transition>
            <v-row v-show="expanded">
                <v-col cols="12" class="pt-0">
                    <slot></slot>
                </v-col>
            </v-row>
        </v-expand-transition>
    </div>
</template>

<script>
const STORAGE_PREFIX = 'home-section-collapsed:';

export default {
    name: 'HomeSectionCard',
    props: {
        icon: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        // 每个卡片的唯一标识，用于在 localStorage 中记住上次的展开/收起状态
        storageKey: {
            type: String,
            required: true,
        },
        defaultExpanded: {
            type: Boolean,
            default: true,
        },
    },
    data() {
        return {
            expanded: this.defaultExpanded,
        };
    },
    created() {
        this.expanded = this.loadExpanded();
    },
    mounted() {
        this.$emit('toggle', this.expanded);
    },
    methods: {
        toggle() {
            this.expanded = !this.expanded;
            this.saveExpanded(this.expanded);
            this.$emit('toggle', this.expanded);
        },
        loadExpanded() {
            try {
                const val = window.localStorage.getItem(STORAGE_PREFIX + this.storageKey);
                if (val === null) {
                    return this.defaultExpanded;
                }
                return val === '1';
            } catch (e) {
                return this.defaultExpanded;
            }
        },
        saveExpanded(val) {
            try {
                window.localStorage.setItem(STORAGE_PREFIX + this.storageKey, val ? '1' : '0');
            } catch (e) {
                // ignore (privacy mode / storage disabled)
            }
        },
    },
};
</script>

<style>
.home-section-card {
    background: rgba(245, 255, 248, 0.8);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border-radius: 10px !important;
    padding: 12px 16px 16px;
    margin-top: 5px;
    margin-bottom: 15px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.theme--dark .home-section-card {
    background: rgba(0, 0, 0, 0.8);
}

/* 收起时不出现第二行 v-row，用与 padding-top 对称的 padding-bottom 让标题行在卡片内垂直居中，
   同时在标题下方留出一点呼吸空间 */
.home-section-card--collapsed {
    padding-bottom: 12px;
}

.home-section-card-header {
    cursor: pointer;
}
</style>
