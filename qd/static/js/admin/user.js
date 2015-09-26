$(function() {
  // 删除用户
  $('body').on('click', '[name=delete]', function (e) {
    var tds = $(this).parent().parent().children();
    var user = $(tds[0]).text();
    var name = $(tds[1]).text();
    if (confirm('确实要删除用户<' + user + '/' + name + 
      '>的资料吗? 删除操作不可撤销')) {
      $.post(
        url_delete_user,
        {user: user},
        ajax_refresh);
    }
  })

  // 编辑用户
  $('body').on('click', '[name=edit]', function (e) {
    var tds = $(this).parent().parent().children();
    var mobile = $(tds[0]).text();
    var username = $(tds[1]).text();
    var is_admin = $(tds[2]).text() == '管理员';
    $('#edit-user input[name=mobile]').val(mobile);
    $('#edit-user input[name=username]').val(username);
    $('#edit-user input[name=password]').val('');
    $('#edit-user input[name=is_admin]').prop('checked', is_admin);
    $('a[href="#edit-user"]').tab('show');
  })

  // 保存
  $('body').on('click', '[name=upsert]', function (e) {
    var params = {
      mobile: $('#edit-user input[name=mobile]').val(),
      username: $('#edit-user input[name=username]').val(),
      password: $('#edit-user input[name=password]').val(),
      is_admin: $('#edit-user input[name=is_admin]').prop('checked'), 
    };
    if (!params.password || !params.mobile || !params.username) {
      alert('手机/姓名/密码都不能为空');
    } else {
      $.post(
        url_upsert_user,
        params,
        ajax_refresh);
    }
  })
});