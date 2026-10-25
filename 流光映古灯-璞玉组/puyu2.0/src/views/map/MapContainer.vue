<template>
	<div id="containerm"></div>
</template>

<script setup>
	import {
		onMounted,
		onUnmounted,
		ref,
		watch
	} from "vue";
	import AMapLoader from "@amap/amap-jsapi-loader";
	import axios from 'axios';

	// 接收筛选条件作为props
	const props = defineProps({
		filterDynasty: {
			type: String,
			default: ""
		}
	});

	let map = null;
	let markers = []; // 存储所有标记实例
	let greenDotIcon = null;
	const maplamp = ref([]); // 从后端获取的地图灯具数据

	// 从后端获取地图灯具数据
	const fetchMapData = async () => {
		try {
			const res = await axios.get('/api/map');
			if (res.status === 200) {
				maplamp.value = res.data;
			} else {
				throw new Error('响应状态错误: ' + res.status);
			}
		} catch (error) {
			// 静默处理错误，使用默认数据
			console.warn('Failed to fetch map data:', error);
			maplamp.value = [];
		}
	};

	// 创建所有标记
	const createMarkers = (AMapInstance) => {
		// 清除现有标记
		markers.forEach(marker => {
			marker.remove();
		});
		markers = [];

		// 根据筛选条件过滤灯具
		let filteredLamps;
		if (props.filterDynasty === '其他') {
			// 选择"其他"时，只显示没有朝代或朝代为空的灯具
			filteredLamps = maplamp.value.filter(lamp => !lamp.dynasty || lamp.dynasty === '');
		} else if (props.filterDynasty) {
			// 选择特定朝代时，只显示该朝代的灯具
			filteredLamps = maplamp.value.filter(lamp => lamp.dynasty === props.filterDynasty);
		} else {
			// 未选择时显示所有灯具
			filteredLamps = maplamp.value;
		}

		// 为每个符合条件的灯具创建标记
		filteredLamps.forEach(item => {
			const marker = new AMapInstance.Marker({
				position: new AMapInstance.LngLat(item.lnglat[0], item.lnglat[1]),
				icon: greenDotIcon,
				title: item.name,
				offset: new AMapInstance.Pixel(-10, -10)
			});
			
			// 添加点击事件
			marker.on('click', function() {
				// 创建信息窗口内容
				const infoWindowContent = `
					<div class="custom-info-window" style="width: 250px; padding: 10px; font-family: Arial, sans-serif;">
						<h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px;">${item.name}</h3>
						<div class="info-window-image" style="margin-bottom: 10px; max-height: 200px; overflow: hidden;">
						<img src="${item.image}" alt="${item.name}" onerror="this.src='http://localhost:5000/static/images/logo.jpg'" style="width: 100%; height: auto; max-height: 200px; object-fit: contain; border: 1px solid #eee; border-radius: 4px;">
					</div>
						<p class="info-window-description" style="margin: 0; font-size: 12px; color: #666; line-height: 1.5;">${item.description}</p>
					</div>
				`;
				
				// 创建并显示信息窗口
				const infoWindow = new AMapInstance.InfoWindow({
					content: infoWindowContent,
					offset: new AMapInstance.Pixel(0, -30)
				});
				
				infoWindow.open(map, marker.getPosition());
			});
			
			map.add(marker);
			markers.push(marker);
		});
	};

	onMounted(async () => {
		// 先获取地图灯具数据
		await fetchMapData();
		if (!import.meta.env.VITE_AMAP_KEY || !import.meta.env.VITE_AMAP_SECURITY_CODE) {
			console.warn('请先配置 VITE_AMAP_KEY 和 VITE_AMAP_SECURITY_CODE');
			return;
		}
		
		window._AMapSecurityConfig = {
			securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
		};
		AMapLoader.load({
				key: import.meta.env.VITE_AMAP_KEY, // 申请好的Web端开发者Key，首次调用 load 时必填
				version: "2.0", // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
				plugins: ["AMap.Scale","AMap.ToolBar"], //需要使用的的插件列表，如比例尺'AMap.Scale'，支持添加多个如：['...','...']
			})
			.then((AMap) => {
					map = new AMap.Map("containerm", {
						// 设置地图容器id
						viewMode: "2D", // 是否为3D地图模式
						zoom: 5, // 初始化地图级别，调整为更适合中国地图的级别
						center: [104.1954, 35.8617], // 调整为中国中心点
						mapStyle: "amap://styles/whitesmoke",
					});
					var toolbar = new AMap.ToolBar(); //创建工具条插件实例
					map.addControl(toolbar); //添加工具条插件到页面
					var Scale = new AMap.Scale(); //创建工具条插件实例
					map.addControl(Scale); //添加工具条插件到页面
					
					// 创建自定义绿色圆点图标
					greenDotIcon = new AMap.Icon({
						size: new AMap.Size(20, 20), // 图标尺寸
						type: 'image',
						image: 'data:image/svg+xml;utf-8,' + encodeURIComponent(`
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20">
								<circle cx="10" cy="10" r="8" fill="#8B5A2B" stroke="#ffffff" stroke-width="2"/>
							</svg>
						`),
						offset: new AMap.Pixel(-10, -10) // 图标偏移量
					});

					// 创建初始标记
					createMarkers(AMap);
				})
			.catch((e) => {
					console.log(e);
				});
	});

	// 监听筛选条件变化，更新标记
	watch(() => props.filterDynasty, async () => {
		if (map) {
			// 重新获取数据
			await fetchMapData();
			// 重新加载地图来应用筛选，因为需要访问AMap实例
			window._AMapSecurityConfig = {
				securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
			};
			AMapLoader.load({
					key: import.meta.env.VITE_AMAP_KEY,
					version: "2.0",
					plugins: ["AMap.Scale","AMap.ToolBar"],
				})
				.then((AMap) => {
						createMarkers(AMap);
					})
				.catch((e) => {
						console.log(e);
					});
		}
	});

	onUnmounted(() => {
		map?.destroy();
	});
</script>

<style scoped>
	#containerm {
		padding: 0px;
		margin: 0px;
		width: 100%;
		height: 100%;
		position: relative;
	}
</style>