module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/dist/css/output.css");
  eleventyConfig.addPassthroughCopy("src/index.html");
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  return {
    dir: {
      input: "src",
      output: "_site",
    },
  };
};
