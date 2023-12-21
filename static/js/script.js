function get_posts(username) {
    if (username === undefined) {
        username = '';
    }
    $('#post-box').empty();
    $.ajax({
        type: 'POST',
        url: `/get_posts?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response['result'] === 'success') {
                let posts = response['posts'];
                posts.forEach(post => {
                    let time_post = new Date(post['date']);
                    let time_before = time2str(time_post);
                    let class_heart = post['heart-by-me'] ? 'fa-heart' : 'fa-heart-o';
                    let class_thumbs = post['thumbs-by-me'] ? 'fa-thumbs-up' : 'fa-thumbs-o-up';
                    let class_star = post['star-by-me'] ? 'fa-star' : 'fa-star-o';

                    let html_temp = `
                            <div class="box" id="${post._id}">
                                <article class="media">
                                    <div class="media-left">
                                        <a href="/user/${post['id']}" class="image is-64x64">
                                            <img src="/static/${post['profile_pic']}" alt=""
                                                class="is-rounded">
                                        </a>
                                    </div>
                                    <div class="media-content">
                                        <div class="content">
                                            <p>
                                                <strong>${post.username}</strong>
                                                <small>@${post.id}</small>
                                                <small>${time_before}</small>
                                                <br>
                                                ${post['comment']}
                                            </p>
                                        </div>
                                        <nav class="level is-mobile">
                                            <div class="level-left">
                                                <a class="level-item is-xander" aria-label="heart" onclick="toggle_like('${post["_id"]}', 'heart')">
                                                    <span class="icon is-small">
                                                        <i class="fa ${class_heart}" aria-hidden="true"></i>
                                                    </span>
                                                    &nbsp;
                                                    <span class="total-num">${num2str(post['count_heart'])}</span>
                                                </a>
                                                <a class="level-item is-xander" aria-label="thumbs" onclick="toggle_thumbs('${post["_id"]}', 'thumbs')">
                                                    <span class="icon is-small">
                                                        <i class="fa ${class_thumbs}" aria-hidden="true"></i>
                                                    </span>
                                                    &nbsp;
                                                    <span class="total-num">${num2str(post['count_thumbs'])}</span>
                                                </a>
                                                <a class="level-item is-xander" aria-label="star" onclick="toggle_star('${post["_id"]}', 'star')">
                                                    <span class="icon is-small">
                                                        <i class="fa ${class_star}" aria-hidden="true"></i>
                                                    </span>
                                                    &nbsp;
                                                    <span class="total-num">${num2str(post['count_star'])}</span>
                                                </a>
                                            </div>
                                        </nav>
                                    </div>
                                </article>
                            </div>
                            `;
                    $('#post-box').append(html_temp);
                });
            }
        }
    });
}

function time2str(date) {
    let today = new Date();
    let time = (today - date) / 1000 / 60;
    
    if (time < 60) return parseInt(time) + ' minutes ago';
    time = time / 60;
    if (time < 24) return parseInt(time) + ' hours ago';
    time = time / 24;
    if (time < 7) return parseInt(time) + ' days ago';

    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    let day = date.getDate();
    return `${year}.${month}.${day}`
}

function num2str(count) {
    if (count > 10000) return parseInt(count / 1000 + 'k');
    if (count > 500) return parseInt(count / 100) / 10 + 'k';
    if (count == 0) return '';
    return count;
}

function toggle_like(post_id, type) {
    let $a_like = $(`#${post_id} a[aria-label='heart']`);
    let $i_like = $a_like.find('i');

    if ($i_like.hasClass('fa-heart')) {
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                'post_id_give': post_id,
                'type_give': type,
                'action_give': 'remove'
            },
            success: function (response) {
                $i_like.removeClass('fa-heart').addClass('fa-heart-o');
                $a_like.find('span.total-num').text(num2str(response['count']));
            }
        });
    } else {
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                'post_id_give': post_id,
                'type_give': type,
                'action_give': 'add'
            },
            success: function (response) {
                $i_like.removeClass('fa-heart-o').addClass('fa-heart');
                $a_like.find('span.total-num').text(num2str(response['count']));
            }
        });
    }
}

function toggle_thumbs(post_id, type) {
    let $a_like = $(`#${post_id} a[aria-label='thumbs']`);
    let $i_like = $a_like.find('i');

    if ($i_like.hasClass('fa-thumbs-up')) {
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                'post_id_give': post_id,
                'type_give': type,
                'action_give': 'remove'
            },
            success: function (response) {
                $i_like.removeClass('fa-thumbs-up').addClass('fa-thumbs-o-up');
                $a_like.find('span.total-num').text(num2str(response['count']));
            }
        });
    } else {
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                'post_id_give': post_id,
                'type_give': type,
                'action_give': 'add'
            },
            success: function (response) {
                $i_like.removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                $a_like.find('span.total-num').text(num2str(response['count']));
            }
        });
    }
}

function toggle_star(post_id, type) {
    let $a_like = $(`#${post_id} a[aria-label='star']`);
    let $i_like = $a_like.find('i');

    if ($i_like.hasClass('fa-star')) {
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                'post_id_give': post_id,
                'type_give': type,
                'action_give': 'remove'
            },
            success: function (response) {
                $i_like.removeClass('fa-star').addClass('fa-star-o');
                $a_like.find('span.total-num').text(num2str(response['count']));
            }
        });
    } else {
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                'post_id_give': post_id,
                'type_give': type,
                'action_give': 'add'
            },
            success: function (response) {
                $i_like.removeClass('fa-star-o').addClass('fa-star');
                $a_like.find('span.total-num').text(num2str(response['count']));
            }
        });
    }
}

function post() {
    let comment = $('#textarea-post').val();
    let today = new Date().toISOString();
    $.ajax({
        type: 'POST',
        url: '/posting',
        data: {
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            $('#modal-post').removeClass('is-active');
            window.location.reload();
        }
    })
}

function update_profile() {
    let name = $('#input-name').val();
    let file = $('#input-pic')[0].files[0];
    let about = $('#textarea-about').val();
    let form_data = new FormData();
    form_data.append('file_give', file);
    form_data.append('name_give', name);
    form_data.append('about_give', about);

    $.ajax({
        type: 'POST',
        url: '/update_profile',
        data: form_data,
        cache: false,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response['result'] === 'success') {
                alert(response['msg']);
                window.location.reload();
            }
        }
    })
}

function logout() {
    $.removeCookie('mytoken');
    alert('You have been logged out!');
    window.location.href = '/auth';
}