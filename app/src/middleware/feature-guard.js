// 功能模块总开关（书单 ENABLE_BOOKLISTS / 有声书 ENABLE_AUDIOBOOKS / 实体书
// ENABLE_PHYSICAL_BOOKS）的全站路由守卫：模块关闭时把该模块的页面弹回首页。
// 关闭只做前端隐藏（后端 API 不拦截），这里的职责和 require-login 一样只管 UX：
// 菜单/按钮的隐藏在各组件里完成，守卫负责"直达 URL"这一层。
//
// 判定数据来自 /user/info 的 sys.allow（$ensureSession 自带拉取与 60 秒缓存）；
// 拿不到快照（超时/旧后端）或字段缺失时一律放行，避免误弹首页。
const MODULE_MATCHERS = [
  {
    flag: "booklists",
    match: (p) =>
      p === "/booklist" || p.startsWith("/booklist/") ||
      p === "/booklists" || p.startsWith("/booklists/"),
  },
  {
    flag: "audiobooks",
    match: (p) => p === "/audiobooks" || p === "/audio" || p.startsWith("/audio/"),
  },
  {
    flag: "physical_books",
    match: (p) => p === "/printbooks",
  },
];

export default async function ({ app, route, redirect }) {
    if (process.server) {
        return;
    }
    const path = (route.path || "/").replace(/\/+$/, "") || "/";
    const hit = MODULE_MATCHERS.find((m) => m.match(path));
    if (!hit) {
        return;
    }
    const info = await app.$ensureSession();
    const allow = info && info.sys && info.sys.allow;
    // 明示 false 才拦截；undefined（旧后端/超时）按开启处理，失败开放
    if (allow && allow[hit.flag] === false) {
        redirect("/");
    }
}