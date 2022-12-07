const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

// With JSDoc @type annotations, IDEs can provide config autocompletion
/** @type {import('@docusaurus/types').DocusaurusConfig} */
(
  module.exports = {
    title: "ConfianceAI Docs",
    tagline: "ConfianceAI DevSecOps technical documentation",
    url: "https://docs.apps.confianceai-public.irtsysx.fr",
    baseUrl: "/",
    onBrokenLinks: "throw",
    onBrokenMarkdownLinks: "warn",
    favicon: "img/favicon.ico",
    organizationName: "ec1", // Usually your GitHub org/user name.
    projectName: "docusaurus", // Usually your repo name.

    plugins: [
      [
        require.resolve("@cmfcmf/docusaurus-search-local"),
        {
          indexBlog: false,
        },
      ],
    ],
    presets: [
      [
        "@docusaurus/preset-classic",
        /** @type {import('@docusaurus/preset-classic').Options} */
        ({
          docs: {
            sidebarPath: require.resolve("./sidebars.js"),
            // Please change this to your repo.
            editUrl:
              "https://git.irt-systemx.fr/confianceai/ec_1/fa2_webapps/docusaurus/edit/master/",
            routeBasePath: "/",
          },
          blog: false,
          theme: {
            customCss: require.resolve("./src/css/custom.css"),
          },
        }),
      ],
    ],

    themeConfig:
      /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
      ({
        navbar: {
          title: "ConfianceAI Docs",
          logo: {
            alt: "ConfianceAI Docs Logo",
            src: "img/logo.jpg",
          },
          items: [
            {
              type: "doc",
              docId: "intro",
              position: "left",
              label: "Docs",
            },
          ],
        },
        footer: {
          style: "dark",
          links: [
            {
              title: "Docs",
              items: [
                {
                  label: "Intro",
                  to: "/intro",
                },
              ],
            },
            {
              title: "Docusaurus",
              items: [
                {
                  label: "GitHub",
                  href: "https://github.com/facebook/docusaurus",
                },
                {
                  label: "Official doc",
                  href: "https://docusaurus.io/docs",
                },
              ],
            },
            {
              title: "Confiance.AI",
              items: [
                {
                  label: "Gitlab",
                  href: "https://git.irt-systemx.fr/confianceai/ec_1/fa2_webapps/docusaurus",
                },
                {
                  label: "Wiki",
                  href: "https://wiki.confiance.ai",
                },
              ],
            },
          ],
          copyright: `Confiance.AI Tools by <a href="https://git.irt-systemx.fr/confianceai/ec_1">team EC1</a>. Built with Docusaurus.`,
        },
        docs: {
          sidebar: {
            hideable: true,
          },
        },
        colorMode: {
          defaultMode: "dark",
          disableSwitch: false,
        },
        prism: {
          theme: require("prism-react-renderer/themes/github"),
          darkTheme: require("prism-react-renderer/themes/palenight"),
        },
      }),
  }
);
