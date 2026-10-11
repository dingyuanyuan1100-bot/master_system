from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.goods import goods_crud
from app.db.db_init import get_db
from app.schemas.goods import GoodsCreate, GoodsResponse

router = APIRouter(prefix="/goods", tags=["商品"])


# 1. 新增商品
@router.post("", response_model=GoodsResponse, status_code=status.HTTP_201_CREATED) #response_model规定返回的数据格式
async def create_goods(data: GoodsCreate, db: AsyncSession = Depends(get_db)):            #data声明要装一个GoodsCreate自定义类（校验）,调用会话生成器生成一个会话实例。默认值写 Depends(xxx)，才会触发依赖注入，让它每一次 HTTP 请求单独执行一次 get_db
    return await goods_crud.create(db = db, obj_in=data.model_dump())                     #调用创建函数，填入db实例，将前端传过来的数据通过model_dump()转化为dict格式


# 2. 根据id查单个商品
@router.get("/{goods_id}", response_model=GoodsResponse)
async def get_goods(goods_id: int, db: AsyncSession = Depends(get_db)):
    goods = await goods_crud.get_by_id(db, id=goods_id)
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")
    return goods

# 3. 分页查商品列表
@router.get("", response_model=List[GoodsResponse])
async def list_goods(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await goods_crud.get_multi(db, skip=skip, limit=limit)


# 4. 更新商品
@router.put("/{goods_id}", response_model=GoodsResponse)
async def update_goods(goods_id: int, data: GoodsCreate, db: AsyncSession = Depends(get_db)):
    goods = await goods_crud.get_by_id(db, id=goods_id)
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")
    return await goods_crud.update(db, db_obj=goods, obj_in=data.model_dump())


# 5. 删除商品
@router.delete("/{goods_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goods(goods_id: int, db: AsyncSession = Depends(get_db)):
    goods = await goods_crud.get_by_id(db, id=goods_id)
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")
    await goods_crud.delete(db, db_obj=goods)
