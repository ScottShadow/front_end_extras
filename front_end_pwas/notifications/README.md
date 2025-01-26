this repo explores the notification api through a simple game of tag

#installation
npm install


#usage
npm run host | python src/server.py

navigate to http://localhost:8080/group-tag

register your name and click on group members name to tag them
you will receive notification when the tag is successful to you or the other person
when tagging you can fail (50%chance) and have to wait to tag again

#notes
built with:
npm install -D @11ty/eleventy tailwindcss @tailwindcss/cli postcss autoprefixer

directory

src
├── css
│   └── tailwind.css
├── dist
│   └── css
│       └── output.css
├── js
│   └── app.js
├── group-tag.njk
├── index.html
└── server.py

