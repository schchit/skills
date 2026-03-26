/**
 * 几何分析模块
 * 封装 WASM 的所有几何分析功能
 */

const { initWasm } = require('./wasm-adapter');
const {
  GeometryType,
  readPoints,
  writePoints,
  extractPolygonFromRegion,
  extractLineFromGeoLine,
  parseGeoJSON,
  createFeature
} = require('./geojson');

/**
 * 根据 GeoJSON 创建 WASM 几何对象
 * @param {Object} Module - WASM 模块实例
 * @param {string} type - 几何类型
 * @param {Array} coordinates - 坐标数组
 * @returns {Object} { geometryPtr, geometryType, cleanup }
 */
function createGeometryFromGeoJSON(Module, type, coordinates) {
  let geometryPtr = null;
  let geometryType = null;
  let cleanup = () => {};

  switch (type) {
    case 'Point': {
      geometryPtr = Module._UGCWasm_GeoPoint_New();
      Module._UGCWasm_GeoPoint_SetX(geometryPtr, coordinates[0]);
      Module._UGCWasm_GeoPoint_SetY(geometryPtr, coordinates[1]);
      geometryType = GeometryType.POINT;
      cleanup = () => Module._UGCWasm_GeoPoint_Delete(geometryPtr);
      break;
    }

    case 'LineString': {
      geometryPtr = Module._UGCWasm_GeoLine_New();
      geometryType = GeometryType.LINESTRING;

      const pointCount = coordinates.length;
      const bufferSize = pointCount * 2 * 8;
      const bufferPtr = Module._malloc(bufferSize);

      try {
        writePoints(Module, bufferPtr, coordinates);
        Module._UGCWasm_GeoLine_AddPart2(geometryPtr, bufferPtr, pointCount);
      } finally {
        Module._free(bufferPtr);
      }

      cleanup = () => Module._UGCWasm_GeoLine_Delete(geometryPtr);
      break;
    }

    case 'MultiLineString': {
      geometryPtr = Module._UGCWasm_GeoLine_New();
      geometryType = GeometryType.LINESTRING;

      for (const lineCoords of coordinates) {
        const pointCount = lineCoords.length;
        const bufferSize = pointCount * 2 * 8;
        const bufferPtr = Module._malloc(bufferSize);

        try {
          writePoints(Module, bufferPtr, lineCoords);
          Module._UGCWasm_GeoLine_AddPart2(geometryPtr, bufferPtr, pointCount);
        } finally {
          Module._free(bufferPtr);
        }
      }

      cleanup = () => Module._UGCWasm_GeoLine_Delete(geometryPtr);
      break;
    }

    case 'Polygon': {
      geometryPtr = Module._UGCWasm_GeoRegion_New();
      geometryType = GeometryType.POLYGON;

      for (const ringCoords of coordinates) {
        const pointCount = ringCoords.length;
        const bufferSize = pointCount * 2 * 8;
        const bufferPtr = Module._malloc(bufferSize);

        try {
          writePoints(Module, bufferPtr, ringCoords);
          Module._UGCWasm_GeoRegion_AddPart2(geometryPtr, bufferPtr, pointCount);
        } finally {
          Module._free(bufferPtr);
        }
      }

      cleanup = () => Module._UGCWasm_GeoRegion_Delete(geometryPtr);
      break;
    }

    case 'MultiPolygon': {
      geometryPtr = Module._UGCWasm_GeoRegion_New();
      geometryType = GeometryType.POLYGON;

      for (const polygonCoords of coordinates) {
        for (const ringCoords of polygonCoords) {
          const pointCount = ringCoords.length;
          const bufferSize = pointCount * 2 * 8;
          const bufferPtr = Module._malloc(bufferSize);

          try {
            writePoints(Module, bufferPtr, ringCoords);
            Module._UGCWasm_GeoRegion_AddPart2(geometryPtr, bufferPtr, pointCount);
          } finally {
            Module._free(bufferPtr);
          }
        }
      }

      cleanup = () => Module._UGCWasm_GeoRegion_Delete(geometryPtr);
      break;
    }

    case 'MultiPoint': {
      // 将 MultiPoint 转换为多个点后处理
      // 对于凸包等操作，可以将多点视为一个点集
      geometryPtr = Module._UGCWasm_GeoRegion_New();
      geometryType = GeometryType.POLYGON;

      // 将所有点作为一个环添加
      const pointCount = coordinates.length;
      const bufferSize = pointCount * 2 * 8;
      const bufferPtr = Module._malloc(bufferSize);

      try {
        writePoints(Module, bufferPtr, coordinates);
        // 注意：对于凸包计算，我们需要使用 GeoLine 而不是 GeoRegion
        // 但 WASM 可能需要不同的处理方式
        Module._UGCWasm_GeoRegion_AddPart2(geometryPtr, bufferPtr, pointCount);
      } finally {
        Module._free(bufferPtr);
      }

      cleanup = () => Module._UGCWasm_GeoRegion_Delete(geometryPtr);
      break;
    }

    default:
      throw new Error(`不支持的几何类型: ${type}`);
  }

  return { geometryPtr, geometryType, cleanup };
}

/**
 * 从 WASM 几何对象提取 GeoJSON
 * @param {Object} Module - WASM 模块实例
 * @param {number} geomPtr - 几何对象指针
 * @param {number} geomType - 几何类型
 * @returns {Object} GeoJSON Geometry
 */
function extractGeometryResult(Module, geomPtr, geomType) {
  if (!geomPtr) return null;

  switch (geomType) {
    case GeometryType.POINT: {
      const x = Module._UGCWasm_GeoPoint_GetX(geomPtr);
      const y = Module._UGCWasm_GeoPoint_GetY(geomPtr);
      return { type: 'Point', coordinates: [x, y] };
    }
    case GeometryType.LINESTRING: {
      const coordinates = extractLineFromGeoLine(Module, geomPtr);
      if (!coordinates || coordinates.length === 0) return null;
      if (coordinates.length === 1) {
        return { type: 'LineString', coordinates: coordinates[0] };
      }
      return { type: 'MultiLineString', coordinates };
    }
    case GeometryType.POLYGON: {
      const coordinates = extractPolygonFromRegion(Module, geomPtr);
      if (!coordinates || coordinates.length === 0) return null;
      if (coordinates.length === 1) {
        return { type: 'Polygon', coordinates: coordinates[0] };
      }
      return { type: 'MultiPolygon', coordinates: coordinates.map(c => [c]) };
    }
    default:
      return null;
  }
}

// ==================== 几何分析函数 ====================

/**
 * 缓冲区分析
 */
async function buffer(input, radius) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  const { geometryPtr, cleanup } = createGeometryFromGeoJSON(Module, type, coordinates);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Buffer(geometryPtr, radius);
    if (!resultPtr) throw new Error('缓冲区分析失败');

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, { ...properties, bufferRadius: radius });
  } finally {
    cleanup();
  }
}

/**
 * 凸多边形计算
 */
async function computeConvexHull(input) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  // 对于 MultiPoint，需要创建 GeoLine 而不是 GeoRegion
  let geometryPtr, cleanup;
  
  if (type === 'MultiPoint') {
    geometryPtr = Module._UGCWasm_GeoLine_New();
    const pointCount = coordinates.length;
    const bufferSize = pointCount * 2 * 8;
    const bufferPtr = Module._malloc(bufferSize);

    try {
      writePoints(Module, bufferPtr, coordinates);
      Module._UGCWasm_GeoLine_AddPart2(geometryPtr, bufferPtr, pointCount);
    } finally {
      Module._free(bufferPtr);
    }
    cleanup = () => Module._UGCWasm_GeoLine_Delete(geometryPtr);
  } else {
    const geom = createGeometryFromGeoJSON(Module, type, coordinates);
    geometryPtr = geom.geometryPtr;
    cleanup = geom.cleanup;
  }
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_ComputeConvexHull(geometryPtr);
    if (!resultPtr) throw new Error('凸包计算失败');

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, properties);
  } finally {
    cleanup();
  }
}

/**
 * 重采样分析
 */
async function resample(input, tolerance) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  const { geometryPtr, geometryType, cleanup } = createGeometryFromGeoJSON(Module, type, coordinates);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Resample(geometryPtr, tolerance);
    if (!resultPtr) throw new Error('重采样失败');

    const resultGeometry = extractGeometryResult(Module, resultPtr, geometryType);
    Module._UGCWasm_GeoLine_Delete(resultPtr);

    return createFeature(resultGeometry, { ...properties, tolerance });
  } finally {
    cleanup();
  }
}

/**
 * 线要素光滑分析
 */
async function smooth(input, smoothness) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  const { geometryPtr, geometryType, cleanup } = createGeometryFromGeoJSON(Module, type, coordinates);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Smooth(geometryPtr, smoothness);
    if (!resultPtr) throw new Error('光滑分析失败');

    const resultGeometry = extractGeometryResult(Module, resultPtr, geometryType);
    Module._UGCWasm_GeoLine_Delete(resultPtr);

    return createFeature(resultGeometry, { ...properties, smoothness });
  } finally {
    cleanup();
  }
}

/**
 * 计算测地线距离
 */
async function computeGeodesicDistance(input, majorAxis = 6378137, flatten = 0.003352810664) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  const { geometryPtr, cleanup } = createGeometryFromGeoJSON(Module, type, coordinates);
  
  try {
    const distance = Module._UGCWasm_Geometrist_ComputeGeodesicDistance(geometryPtr, majorAxis, flatten);
    return { type: 'Result', distance, unit: 'meters', properties };
  } finally {
    cleanup();
  }
}

/**
 * 计算测地线面积
 */
async function computeGeodesicArea(input, majorAxis = 6378137, flatten = 0.003352810664) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  const { geometryPtr, cleanup } = createGeometryFromGeoJSON(Module, type, coordinates);
  
  try {
    const area = Module._UGCWasm_Geometrist_ComputeGeodesicArea(geometryPtr, majorAxis, flatten);
    return { type: 'Result', area, unit: 'square_meters', properties };
  } finally {
    cleanup();
  }
}

/**
 * 几何对象是否相交
 */
async function hasIntersection(input1, input2, tolerance = 0) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1 } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const result = Module._UGCWasm_Geometrist_HasIntersection(geom1.geometryPtr, geom2.geometryPtr, tolerance);
    return { type: 'Result', hasIntersection: result === 1 };
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 几何对象边界是否接触
 */
async function hasTouch(input1, input2, tolerance = 0) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1 } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const result = Module._UGCWasm_Geometrist_HasTouch(geom1.geometryPtr, geom2.geometryPtr, tolerance);
    return { type: 'Result', hasTouch: result === 1 };
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 几何对象相等分析
 */
async function isIdentical(input1, input2, tolerance = 0) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1 } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const result = Module._UGCWasm_Geometrist_IsIdentical(geom1.geometryPtr, geom2.geometryPtr, tolerance);
    return { type: 'Result', isIdentical: result === 1 };
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 相交分析
 */
async function intersect(input1, input2) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1, properties } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Intersect(geom1.geometryPtr, geom2.geometryPtr);
    if (!resultPtr) return null;

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, properties);
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 合并分析
 */
async function union(input1, input2) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1, properties } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Union(geom1.geometryPtr, geom2.geometryPtr);
    if (!resultPtr) return null;

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, properties);
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 擦除分析
 */
async function erase(input1, input2) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1, properties } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Erase(geom1.geometryPtr, geom2.geometryPtr);
    if (!resultPtr) return null;

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, properties);
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 异或分析
 */
async function xor(input1, input2) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1, properties } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_XOR(geom1.geometryPtr, geom2.geometryPtr);
    if (!resultPtr) return null;

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, properties);
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 裁剪分析
 */
async function clip(input1, input2) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1, properties } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_Clip(geom1.geometryPtr, geom2.geometryPtr);
    if (!resultPtr) return null;

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.POLYGON);
    Module._UGCWasm_GeoRegion_Delete(resultPtr);

    return createFeature(resultGeometry, properties);
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 计算距离
 */
async function distance(input1, input2) {
  const parsed1 = typeof input1 === 'string' ? JSON.parse(input1) : input1;
  const parsed2 = typeof input2 === 'string' ? JSON.parse(input2) : input2;
  const { type: type1, coordinates: coords1 } = parseGeoJSON(parsed1);
  const { type: type2, coordinates: coords2 } = parseGeoJSON(parsed2);
  const Module = await initWasm();

  const geom1 = createGeometryFromGeoJSON(Module, type1, coords1);
  const geom2 = createGeometryFromGeoJSON(Module, type2, coords2);
  
  try {
    const dist = Module._UGCWasm_Geometrist_Distance(geom1.geometryPtr, geom2.geometryPtr);
    return { type: 'Result', distance: dist };
  } finally {
    geom1.cleanup();
    geom2.cleanup();
  }
}

/**
 * 点是否在线的左侧
 */
async function isLeft(point, lineStart, lineEnd) {
  const Module = await initWasm();
  const result = Module._UGCWasm_Geometrist_IsLeft(
    point[0], point[1],
    lineStart[0], lineStart[1],
    lineEnd[0], lineEnd[1]
  );
  return { type: 'Result', isLeft: result === 1 };
}

/**
 * 点是否在线的右侧
 */
async function isRight(point, lineStart, lineEnd) {
  const Module = await initWasm();
  const result = Module._UGCWasm_Geometrist_IsRight(
    point[0], point[1],
    lineStart[0], lineStart[1],
    lineEnd[0], lineEnd[1]
  );
  return { type: 'Result', isRight: result === 1 };
}

/**
 * 点是否在线段上
 */
async function isPointOnLine(point, lineStart, lineEnd, extended = false) {
  const Module = await initWasm();
  const result = Module._UGCWasm_Geometrist_IsPointOnLine(
    point[0], point[1],
    lineStart[0], lineStart[1],
    lineEnd[0], lineEnd[1],
    extended ? 1 : 0
  );
  return { type: 'Result', isPointOnLine: result === 1 };
}

/**
 * 线平行分析
 */
async function isParallel(line1Start, line1End, line2Start, line2End) {
  const Module = await initWasm();
  const result = Module._UGCWasm_Geometrist_IsParallel(
    line1Start[0], line1Start[1], line1End[0], line1End[1],
    line2Start[0], line2Start[1], line2End[0], line2End[1]
  );
  return { type: 'Result', isParallel: result === 1 };
}

/**
 * 计算点到线段的距离
 */
async function distanceToLineSegment(point, lineStart, lineEnd) {
  const Module = await initWasm();
  const dist = Module._UGCWasm_Geometrist_DistanceToLineSegment(
    point[0], point[1],
    lineStart[0], lineStart[1],
    lineEnd[0], lineEnd[1]
  );
  return { type: 'Result', distance: dist };
}

/**
 * 计算平行线
 */
async function computeParallel(input, distance) {
  const parsedInput = typeof input === 'string' ? JSON.parse(input) : input;
  const { type, coordinates, properties } = parseGeoJSON(parsedInput);
  const Module = await initWasm();

  const { geometryPtr, cleanup } = createGeometryFromGeoJSON(Module, type, coordinates);
  
  try {
    const resultPtr = Module._UGCWasm_Geometrist_ComputeParallel(geometryPtr, distance);
    if (!resultPtr) throw new Error('计算平行线失败');

    const resultGeometry = extractGeometryResult(Module, resultPtr, GeometryType.LINESTRING);
    Module._UGCWasm_GeoLine_Delete(resultPtr);

    return createFeature(resultGeometry, { ...properties, distance });
  } finally {
    cleanup();
  }
}

// 导出所有函数
module.exports = {
  // 单几何操作
  buffer,
  computeConvexHull,
  resample,
  smooth,
  computeGeodesicDistance,
  computeGeodesicArea,
  computeParallel,
  
  // 双几何操作
  hasIntersection,
  hasTouch,
  isIdentical,
  intersect,
  union,
  erase,
  xor,
  clip,
  distance,
  
  // 点线关系
  isLeft,
  isRight,
  isPointOnLine,
  isParallel,
  distanceToLineSegment,
  
  // 工具函数
  createGeometryFromGeoJSON,
  extractGeometryResult
};
