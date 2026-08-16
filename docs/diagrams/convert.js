const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const dir = __dirname;
const files = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith(".svg"))
  .sort();

(async () => {
  for (const file of files) {
    const input = path.join(dir, file);
    const output = path.join(dir, file.replace(/\.svg$/i, ".png"));
    await sharp(input, { density: 150 })
      .png({ compressionLevel: 9 })
      .toFile(output);
    const stat = fs.statSync(output);
    console.log(`OK  ${file} ? ${path.basename(output)}  (${Math.round(stat.size / 1024)} KB)`);
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
