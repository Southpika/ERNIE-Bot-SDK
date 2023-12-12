ITEM_LIST_HTML = """<html>
<head>
    <meta charset="UTF-8">
    <title>Colored List</title>
    <style>
        /* 设置第一个 <li> 元素的颜色为红色 */
        ul.custom-list li:last-child {{
            color: green;
        }}
    </style>
</head>
<body>
    <ul class="custom-list">
        {ITEM}
    </ul>
</body>
</html>"""

# IMAGE_HTML = "<img src='data:image/png;base64,{BASE64_ENCODED}' />"

IMAGE_HTML = """
<html>
<body>

  <!-- 图片容器 -->
  <div class="image-container">

    <!-- 图片 -->
    <img src='data:image/png;base64,{BASE64_ENCODED}' />

    <!-- 半透明覆盖层 -->
    <div class="overlay"></div>

    <!-- 可点击的链接 -->
    <a href={IMG_LOCATION} class="image-link" target="_blank">View Image</a>
  </div>

</body>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    /* 定义图像容器 */
    .image-container {{
      position: relative;
      display: inline-block;
    }}

    /* 图片 */
    .image-container img {{
      display: block;
      width: 100%;
      height: auto;
    }}

    /* 半透明覆盖层 */
    .overlay {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
      opacity: 0;
      transition: opacity 0.3s ease;
    }}

    /* 悬停时改变样式 */
    .image-container:hover .overlay {{
      opacity: 1;
    }}

    /* 链接样式 */
    .image-link {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: #fff;
      text-decoration: underline;
      opacity: 0;
      transition: opacity 0.3s ease;
    }}

    /* 悬停时显示链接 */
    .image-container:hover .image-link {{
      opacity: 1;
    }}
  </style>
</head>
</html>"""
