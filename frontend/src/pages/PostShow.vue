<template>
  <div>
    <h1 class="text-3xl mb-10">Blog Post {{ $route.params.id }}</h1>

    <img
      class="mb-10"
      width="400"
      height="225"
      :src="`https://picsum.photos/400/225?${$route.params.id}`"
      alt="Shoes"
    />
    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque sapien diam, sollicitudin
      hendrerit consequat a, malesuada sed odio. Maecenas convallis fermentum placerat. Phasellus
      tempus enim vitae facilisis viverra. Maecenas auctor sollicitudin neque eget pharetra. Ut
      vitae consectetur dui, at interdum justo. In hac habitasse platea dictumst. Phasellus ornare
      venenatis congue. In accumsan libero a laoreet bibendum. Aliquam sed congue urna. Aliquam at
      scelerisque odio. Aenean in turpis vel tortor tristique interdum. Vivamus finibus, orci at
      dapibus fermentum, arcu ante placerat ex, nec tincidunt risus nibh non elit.
    </p>

    <h2 class="text-xl">Heading 2</h2>
    <p>
      Integer non hendrerit massa, in dictum mauris. Suspendisse suscipit eleifend est, nec aliquet
      eros consectetur eget. Pellentesque consectetur ipsum ac purus tempus, porttitor accumsan
      dolor volutpat. Phasellus nisl nisi, tempus sit amet posuere et, dictum vitae leo. Nunc neque
      tortor, tempus quis nisi quis, ornare convallis ipsum. Nulla euismod vel eros ut placerat.
      Proin dui lectus, volutpat non eros sit amet, fringilla sollicitudin metus. Phasellus laoreet,
      ante a ultrices luctus, diam turpis tincidunt enim, at luctus erat nunc vitae neque. Sed
      efficitur dui elementum sagittis varius.
    </p>

    <p>
      Aenean sollicitudin fermentum sem quis feugiat. Duis pharetra dignissim quam, eu dictum dolor
      vehicula vitae. Morbi diam nisl, viverra sed nulla sed, finibus aliquet sem. Suspendisse
      maximus laoreet euismod. Proin ut posuere tortor. Etiam eleifend nisl sed pulvinar pulvinar.
      Donec dignissim velit id mi mattis, sit amet imperdiet purus egestas.
    </p>

    <h2 class="text-xl">Heading 2</h2>
    <p>
      Pellentesque commodo quis dui non elementum. In non lacus vehicula, placerat est ut, interdum
      lorem. Quisque nec sapien vitae tellus interdum euismod. Donec ac mattis mauris. Nam tincidunt
      euismod magna, ac vehicula mi posuere et. Suspendisse tristique ipsum hendrerit, tempus felis
      eget, fermentum tellus. Integer at erat enim. Integer sit amet congue massa, ac mollis sem.
      Sed ultricies elit tortor, ut faucibus massa iaculis nec. Vivamus aliquam augue a vulputate
      porta. Duis viverra turpis aliquet feugiat cursus. Integer convallis mi non enim imperdiet
      ornare. Nulla posuere iaculis justo, in mollis elit malesuada et.
    </p>

    <p>
      Vestibulum sit amet tortor lacinia, pulvinar ipsum sed, rhoncus lectus. Donec suscipit odio et
      sodales egestas. Suspendisse mattis odio eu sapien luctus, nec molestie nisi tincidunt. Donec
      ligula eros, faucibus sit amet maximus nec, euismod in sapien. Interdum et malesuada fames ac
      ante ipsum primis in faucibus. Sed tincidunt elementum sem, et vestibulum nulla lacinia at.
      Maecenas sed malesuada ipsum. Suspendisse potenti.
    </p>
  </div>
</template>

<style scoped>
p {
  margin-bottom: 10px;
}
</style>
