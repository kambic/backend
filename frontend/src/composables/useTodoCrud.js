// composables/useTodoCrud.ts
import { useTodoStore } from "../stores/todoStore";
import { ref, watch } from "vue";

export function useTodoCrud() {
  const store = useTodoStore();
  const modalOpen = ref(false);
  const editingTodo = ref(null);
  const formTitle = ref("");

  const openCreate = () => {
    editingTodo.value = null;
    formTitle.value = "";
    modalOpen.value = true;
  };

  const openEdit = (todo) => {
    editingTodo.value = todo;
    formTitle.value = todo.title;
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingTodo.value = null;
    formTitle.value = "";
  };

  const saveTodo = async () => {
    if (!formTitle.value.trim()) return;

    if (editingTodo.value) {
      await store.updateTodo(editingTodo.value.id, { title: formTitle.value });
    } else {
      await store.addTodo(formTitle.value);
    }
    closeModal();
  };

  // Auto-fetch on mount
  watch(
    () => store.todos,
    () => {},
    { immediate: true },
  );
  store.fetchTodos();

  return {
    modalOpen,
    editingTodo,
    formTitle,
    openCreate,
    openEdit,
    closeModal,
    saveTodo,
    deleteTodo: store.deleteTodo,
    todos: store.todos,
    loading: store.loading,
    total: store.total,
    completedCount: store.completedCount,
  };
}
