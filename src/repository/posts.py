import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, File

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.cloudinary import configure_cloudinary
from src.entity.models import Post, User, TagToPost

from src.schemas.post import PostModel
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate
from src.routes.transformation import remove_qrcode


async def get_posts(db: AsyncSession):
    """
    The get_posts function returns a list of the most recent 20 posts.

    :param db: AsyncSession: Pass the database session to the function
    :return: A list of posts
    """
    post = select(Post).order_by(Post.created_at.desc()).limit(20)
    post = await db.execute(post)
    return post.scalars().unique().all()


async def get_post(post_id: int, db: AsyncSession):
    """
    The get_post function takes a post_id and an async database session as arguments.
    It then queries the Post table for the row with that id, and returns it.

    :param post_id: int: Specify the type of parameter that is expected
    :param db: AsyncSession: Pass in the database session to use
    :return: A single post
    """
    post = select(Post).filter(Post.id == post_id)
    post = await db.execute(post)
    return post.scalars().first()


async def get_user_post(post_id: int, current_user: User, db: AsyncSession):
    """
    The get_user_post function is used to get a post by its id.
        Args:
            post_id (int): The id of the post you want to retrieve.
            current_user (User): The user who is making the request for this function.  This will be used to determine if they are an admin or not, and thus whether or not they can see all posts, or just their own posts.
            db (AsyncSession): An async session object that will be used for querying the database with SQLAlchemy Core syntax.

    :param post_id: int: Filter the posts by id
    :param current_user: User: Check if the user is an admin or not
    :param db: AsyncSession: Pass the database session to the function
    :return: A post object with the given id, if it exists
    """
    post = select(Post).filter(Post.id == post_id).filter_by(user=current_user)
    if current_user.user_type_id != 1:
        post = select(Post).filter(Post.id == post_id)
    post = await db.execute(post)
    return post.scalars().first()


async def create_post(body: PostModel, image_url: str, image_id: str, current_user: User, db: AsyncSession):
    """
    The create_post function creates a new post in the database.
        It takes three arguments:
            - body: The PostModel object that contains the name, content and tags of the post to be created.
            - image_url: The url of an image associated with this post (optional).
            - current_user: A User object representing the user who is creating this post.

    :param body: PostModel: Pass the data from the request body to the function
    :param image_url: str: Pass the image url to the database
    :param image_id: str: Store the image id in the database
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the function
    :return: A post object
    """
    post = select(Post).filter_by(user=current_user).filter(Post.name == body.name)
    post = await db.execute(post)
    post = post.scalars().first()
    if post:
        raise HTTPException(status_code=400, detail="Post with this name already exists")
    post = Post(name=body.name, content=body.content, image_url=image_url, image_id=image_id, user=current_user)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    post_id = post.id
    for tag_name in body.tags:
        tag = await get_or_create_tag_by_name(tag_name, db)
        tag_to_post = TagToPost(post_id=post_id, tag_id=tag.id)
        db.add(tag_to_post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(post_id: int, body: PostModel, current_user: User, db: AsyncSession):
    """
    The update_post function updates a post in the database.
        Args:
            post_id (int): The id of the post to update.
            body (PostModel): The new data for the specified Post object.
            current_user (User): The user who is making this request, used to check if they are authorized to make this change.

    :param post_id: int: Identify the post we want to delete
    :param body: PostModel: Get the new values for the post
    :param current_user: User: Check if the user is authorized to update the post
    :param db: AsyncSession: Pass the database session to the function
    :return: A postmodel object
    """
    post = await get_user_post(post_id, current_user, db)
    if post:
        post.name = body.name
        post.content = body.content
        post.image_url = post.image_url

        post.tags.clear()

        for tag_name in body.tags:
            tag = await get_or_create_tag_by_name(tag_name, db)
            tag_to_post = TagToPost(post_id=post_id, tag_id=tag.id)
            db.add(tag_to_post)
        await db.commit()
        await db.refresh(post)
    return post


async def add_tag_to_post(body: TagUpdate, current_user: User, db: AsyncSession) -> Post:
    """
    The add_tag_to_post function adds a tag to the post.
        Args:
            body (TagUpdate): The TagUpdate object containing the name of the post and tags to add.
            current_user (User): The User object representing who is making this request.
            db (AsyncSession): A database session for interacting with Postgresql via SQLAlchemy Core.

    :param body: TagUpdate: Get the name of the post and tags to add
    :param current_user: User: Check if the user is authorized to add tags to a post
    :param db: AsyncSession: Pass the database session to the function
    :return: A post with a new tag
    """
    post = await db.execute(select(Post).where(Post.id == body.post_id))
    post = post.scalar()
    if not post:
        raise HTTPException(status_code=400, detail="Post with this name doesn't exist")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can add tags only for self posts")
    body_tagnames = [bod for bod in body.tags]
    post_tagnames = [tags.name for tags in post.tags]
    post__id = post.id
    for tag_name in body.tags:
        if tag_name in post_tagnames:
            continue
        if len(set(post_tagnames + body_tagnames)) > 5:
            quantity = 5 - len(post.tags)
            raise HTTPException(status_code=400, detail=f"Post can consists maximum 5 tags. You can add: {quantity}")
        tag = await get_or_create_tag_by_name(tag_name, db)
        tag_to_post = TagToPost(post_id=post__id, tag_id=tag.id)
        db.add(tag_to_post)
    await db.commit()
    await db.refresh(post)
    return post


async def remove_post(post_id: int, current_user: User, db: AsyncSession):
    """
    The remove_post function removes a post from the database.
        Args:
            post_id (int): The id of the post to be removed.
            current_user (User): The user who is making this request. This is used to ensure that only the owner of a
            particular post can remove it, and not other users.


    :param post_id: int: Get the post from the database
    :param current_user: User: Ensure that the user is logged in
    :param db: AsyncSession: Connect to the database
    :return: The post that was removed
    """
    await remove_qrcode (post_id, current_user, db)
    post = await get_user_post(post_id, current_user, db)
    post_return = post
    if post:
        configure_cloudinary()
        cloudinary.uploader.destroy(str(post.image_id))
        post.tags.clear()
        await db.commit()
        await db.delete(post)
        await db.commit()
    return post_return
