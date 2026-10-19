export const state = () => ({
    nav: true, loading: true, count: 0, searchLoading: false, user: {
        is_admin: false,
        is_login: false,
        nickname: "",
        kindle_email: "",
        avatar: "",
    }, alert: {
        to: "", msg: "", type: "", show: false,
    }, sys: {
        socials: [],
        allow: {
            physical_books: false,
            // 功能模块总开关在拉取 /user/info 前按"开启"兜底，避免首屏把入口闪没
            booklists: true,
            audiobooks: true,
            download_quota: false,
            upload: false,
            register: false,
            require_login: false,
            guest_read: false,
            guest_download: false,
            guest_upload: false,
            guest_push: false,
            guest_register: false,
            book_review: false
        },
        mynexus_enabled: false
    },
    site_title: "首页",
    site_title_template: "%s | MyBooks",
    showUserInfo: false
})

export const mutations = {
    loading(state) {
        state.loading = true;
    }, loaded(state) {
        state.loading = false;
    }, /*
    puremode(state, pure) {
        if (pure) {
            state.nav = false;
        } else {
            state.nav = true;
        }
    },
    */
    navbar(state, nav) {
        state.nav = nav;
    },
    search_loading(state, loading) {
        state.searchLoading = loading;
    }, increment(state) {
        state.count++
    }, login(state, data) {
        if (data != undefined) {
            if (data.sys) {
                state.sys = data.sys;
            }
            if (data.user) {
                state.user = data.user;
            }
        }
    }, alert(state, v) {
        state.alert.to = v.to;
        state.alert.type = v.type;
        state.alert.msg = v.msg;
        state.alert.show = true;
    }, close_alert(state) {
        state.alert.show = false;
    }, clear_user(state) {
        // 退出登录 / 会话过期（user.need_login）时统一走这里：
        // 全站守卫靠 user.is_login 走快路径，只清插件缓存不清 store 会让过期会话继续放行。
        state.user = {
            is_admin: false,
            is_login: false,
            nickname: "",
            kindle_email: "",
            avatar: "",
        };
    }, settings_title(state, v) {
        state.site_title_template = ' %s | ' + v;
    }
}
