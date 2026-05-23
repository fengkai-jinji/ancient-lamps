<template>
	<div class="map_top">
		中国古灯地图分布图
	</div>
	<div id="map-container">
		<div class="map-container-wrapper">
				<MapContainerVue :filter-dynasty="filterDynasty"/>
			</div>
		<div class="map_right">
			<!-- 描述性文字 -->
			<div class="map-description">
				<p>{{ currentDymain }}</p>
			</div>
			<!-- 照片展示区域 -->
			<div class="photo-display">
				<img
					v-if="currentPhoto"
					:src="currentPhoto"
					:alt="currentPhotoName"
					class="lamp-photo"
					@click="openImageModal(currentPhoto)"
				/>
				<div v-else class="no-photo-message">暂未找到相应的地图</div>

				<!-- 多张地图切换控制，仅在当前朝代存在多张地图时显示 -->
				<div
					v-if="currentDynastyMaps.length > 1"
					class="photo-controls"
				>
					<button
						class="photo-nav-btn"
						@click="prevMap"
						:disabled="currentMapIndex === 0"
					>
						上一张
					</button>
					<div class="photo-dots">
						<span
							v-for="(m, idx) in currentDynastyMaps"
							:key="idx"
							class="photo-dot"
							:class="{ active: idx === currentMapIndex }"
							@click="goToMap(idx)"
						></span>
					</div>
					<button
						class="photo-nav-btn"
						@click="nextMap"
						:disabled="currentMapIndex === currentDynastyMaps.length - 1"
					>
						下一张
					</button>
				</div>
			</div>
			<!-- 筛选下拉列表 -->
			<div class="filter-section">
				<h4>按朝代筛选</h4>
				<div class="filter-dropdown">
					<select v-model="currentPhotoIndex" @change="onDropdownChange" class="dropdown-select">
						<option v-for="(photo, index) in photos" :key="index" :value="index">
							{{ photo.name }}
						</option>
					</select>
				</div>
			</div>
		</div>
	</div>
	
	<!-- 图片放大模态框 -->
	<div v-if="isImageModalOpen" class="image-modal" @click="closeImageModal">
		<div class="modal-content" @click.stop>
			<button class="close-btn" @click="closeImageModal">×</button>
			<img :src="currentModalImage" :alt="currentPhotoName" class="modal-image" @error="handleImageError($event)" />
		</div>
	</div>
</template>
<script setup>
	import { ref, computed } from 'vue';
	import MapContainerVue from './MapContainer.vue';

	// 定义可用的照片数据，支持每个朝代多张地图
	const photos = ref([
		{
			name: '全部灯具',
			dynasty: '',
			maps: [
				{ src: '', dymain: '' } // 可放总览地图
			]
		},
		{
			name: '新石器灯具',
			dynasty: '新石器',
			maps: [
				{ src: '', dymain: '' }
			]
		},
		{
			name: '战国灯具',
			dynasty: '战国',
			maps: [
				{ src: '/src/assets/lamps/zhanguo.jpg', dymain: '公元前476年/公园前403年-公元前220年' }
			]
		},
		{
			name: '西汉灯具',
			dynasty: '西汉',
			maps: [
				{ src: '/src/assets/lamps/xihan.jpg', dymain: '又称前汉，公元前202年-公元8年' }
			]
		},
		{
			name: '东汉灯具',
			dynasty: '东汉',
			maps: [
				{ src: '/src/assets/lamps/donghan.jpg', dymain: '公元25年-公元220年' }
			]
		},
		{
			name: '唐代灯具',
			dynasty: '唐代',
			maps: [
				{ src: '/src/assets/lamps/tang01.jpg', dymain: '下方是669年时唐朝的地图' },
				{ src: '/src/assets/lamps/tang02.jpg', dymain: '下方是741年时唐朝的地图' },
				{ src: '/src/assets/lamps/tang03.jpg', dymain: '下方是820年时唐朝的地图' }
			]
		},
		{
			name: '宋代灯具',
			dynasty: '宋代',
			maps: [
				{ src: '/src/assets/lamps/song01.jpg', dymain: '下方是1111年时北宋的地图' },
				{ src: '/src/assets/lamps/song02.jpg', dymain: '下方是1142年时南宋的地图' },
				{ src: '/src/assets/lamps/song03.jpg', dymain: '下方是1202年时南宋的地图' }
			]
		},
		{
			name: '元代灯具',
			dynasty: '元代',
			maps: [
				{ src: '/src/assets/lamps/yuan.jpg', dymain: '下方是1280年时元代的地图' },
				{ src: '/src/assets/lamps/yuan02.jpg', dymain: '下方是1330年时元代的地图' }
			]
		},
		{
			name: '明代灯具',
			dynasty: '明代',
			maps: [
				{ src: '/src/assets/lamps/ming.jpg', dymain: '下方是1433年时明代的地图' },
				{ src: '/src/assets/lamps/ming02.jpg', dymain: '下方是1582年时明代的地图' }
			]
		},
		{
			name: '清代灯具',
			dynasty: '清代',
			maps: [
				{ src: '/src/assets/lamps/qing.jpg', dymain: '下方是1820年时清代的地图' },
				{ src: '/src/assets/lamps/qing02.jpg', dymain: '下方是1908年时清代的地图' }
			]
		},
		{
			name: '其他朝代灯具',
			dynasty: '其他',
			maps: [
				{ src: '', dymain: '' }
			]
		}
	]);

	// 当前选中的朝代索引
	const currentPhotoIndex = ref(0);

	// 当前朝代下的地图索引（用于同一朝代多张地图切换）
	const currentMapIndex = ref(0);

	// 当前朝代对象
	const currentDynasty = computed(() => photos.value[currentPhotoIndex.value] || photos.value[0]);

	// 当前朝代的所有地图
	const currentDynastyMaps = computed(() => currentDynasty.value?.maps || []);

	// 当前展示的地图信息
	const currentPhoto = computed(() => currentDynastyMaps.value[currentMapIndex.value]?.src || '');
	const currentPhotoName = computed(() => currentDynasty.value?.name || '');
	const currentDymain = computed(() => currentDynastyMaps.value[currentMapIndex.value]?.dymain || '');

// 图片模态框状态
const isImageModalOpen = ref(false);
const currentModalImage = ref('');

	// 计算当前筛选的朝代（传给地图组件）
	const filterDynasty = computed(() => currentDynasty.value.dynasty);

	// 下拉列表变化处理函数
	const onDropdownChange = () => {
		// 每次切换朝代时回到该朝代的第一张地图
		currentMapIndex.value = 0;
	};

	// 切换到指定地图
	const goToMap = (index) => {
		if (index >= 0 && index < currentDynastyMaps.value.length) {
			currentMapIndex.value = index;
		}
	};

	// 上一张地图
	const prevMap = () => {
		if (currentMapIndex.value > 0) {
			currentMapIndex.value -= 1;
		}
	};

	// 下一张地图
	const nextMap = () => {
		if (currentMapIndex.value < currentDynastyMaps.value.length - 1) {
			currentMapIndex.value += 1;
		}
	};

const handleImageError = (e) => {
	e.target.src = 'http://localhost:5000/static/images/logo.jpg';
	console.warn('图片加载失败，已使用默认图片替代');
};

// 打开图片模态框
const openImageModal = (imageSrc) => {
	currentModalImage.value = imageSrc;
	isImageModalOpen.value = true;
	// 禁用背景滚动
	document.body.style.overflow = 'hidden';
};

// 关闭图片模态框
const closeImageModal = () => {
	isImageModalOpen.value = false;
	// 恢复背景滚动
	document.body.style.overflow = '';
};
</script>

<style scoped>
  *{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: '宋体';
  }
	.map_top{
		
		width: 100%;
		height: 20%;
		text-align: center;
		font-size: 40px;
		font-weight: 400;
		font-family:'Ma Shan Zheng';
		padding-top: 35px;
		color:#5d4037;
		
	}
	#map-container{
		display: flex;
		width: 100%;
		height: calc(100vh - 20%);
	}
	.map-container-wrapper {
		flex: 3;
		height: 100%;
	}
	.map_right{
		flex: 1;
		height: 100%;
		padding: 10px;
		background-color: #f8f5f0;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		backdrop-filter: blur(5px);
	}
	/* 照片展示区域 */
	.photo-display {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-direction: column;
		margin-bottom: 15px;
		background-color: rgba(255, 255, 255, 0.8);
		padding: 8px;
		border-radius: 8px;
		border: 1px solid rgba(139, 107, 70, 0.1);
		box-shadow: 0 2px 8px rgba(139, 107, 70, 0.05);
	}
	.lamp-photo {
				max-width: 100%;
				max-height: 80%;
				object-fit: contain;
			}
			.no-photo-message {
				display: flex;
				align-items: center;
				justify-content: center;
				width: 100%;
				height: 100%;
				font-size: 16px;
				color: #999;
				text-align: center;
				padding: 10px;
				background-color: #f5f5f5;
				border: 1px dashed #ddd;
				border-radius: 4px;
			}
	/* 多图切换控件 */
	.photo-controls {
		margin-top: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 10px;
	}

	.photo-nav-btn {
		padding: 4px 10px;
		font-size: 12px;
		border-radius: 12px;
		border: 1px solid rgba(139, 107, 70, 0.4);
		background-color: #f8f5f0;
		color: #5d4037;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.photo-nav-btn:hover:not(:disabled) {
		background-color: #e6d7c3;
	}

	.photo-nav-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.photo-dots {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.photo-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background-color: #d0c4b4;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.photo-dot.active {
		background-color: #8b6b46;
		transform: scale(1.2);
	}
	/* 筛选区域 */
	.filter-section {
		padding: 6px 0;
		background-color: rgba(255, 255, 255, 0.8);
		border-radius: 8px;
		border: 1px solid rgba(139, 107, 70, 0.1);
		box-shadow: 0 2px 8px rgba(139, 107, 70, 0.05);
		padding: 15px;
	}
	.filter-section h4 {
		margin: 0 0 15px 0;
		font-size: 16px;
		color: #5d4037;
		text-align: center;
		
	}
	.filter-dropdown {
		text-align: center;
	}
	.dropdown-select {
		width: 100%;
		max-width: 200px;
		padding: 10px 15px;
		background-color: #f8f5f0;
		border: 1px solid rgba(139, 107, 70, 0.3);
		border-radius: 20px;
		cursor: pointer;
		font-size: 14px;
		color: #8b6b46;
		transition: all 0.3s ease;
		
	}
	.dropdown-select:focus {
		outline: none;
		border-color: #8b6b46;
		box-shadow: 0 0 0 2px rgba(139, 107, 70, 0.25);
	}
	.dropdown-select option {
		padding: 10px;
		background-color: #ffffff;
		color: #5d4037;
		font-family: '宋体';
	}
	
	/* 确保下拉选择框在所有情况下都清晰可见 */
	.dropdown-select {
		background-color: #ffffff !important;
		color: #5d4037 !important;
		border: 1px solid #8b6b46 !important;
	}
	
	.dropdown-select:focus {
		border-color: #5d4037 !important;
		box-shadow: 0 0 0 2px rgba(93, 64, 55, 0.25) !important;
	}
	
	/* 图片放大模态框 */
	.image-modal {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.9);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		cursor: pointer;
	}
	
	.modal-content {
		position: relative;
		max-width: 90%;
		max-height: 90%;
		cursor: default;
	}
	
	.close-btn {
		position: absolute;
		top: -40px;
		right: 0;
		background: none;
		border: none;
		color: white;
		font-size: 30px;
		cursor: pointer;
		padding: 5px;
	}
	
	.close-btn:hover {
		color: #ddd;
	}
	
	.modal-image {
		max-width: 100%;
		max-height: 80vh;
		object-fit: contain;
		border-radius: 4px;
	}
	
	/* 描述性文字 */
	.map-description {
		text-align: center;
		padding: 4px;
	}

	.map-description p {
		margin: 0;
		color: #8b6b46;
		font-size: 14px;
		line-height: 1.4;
		
	}
	
	/* 鼠标悬停效果 */
	.lamp-photo {
		cursor: pointer;
		transition: transform 0.2s ease;
	}
	
	.lamp-photo:hover {
		transform: scale(1.02);
	}
</style>